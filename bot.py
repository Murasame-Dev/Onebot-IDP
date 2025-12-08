"""
Onebot V11 机器人客户端
通过 WebSocket 连接 Onebot 实现，监听消息并处理绑定命令
"""
import asyncio
import json
import re
from typing import Optional, Callable, Awaitable

import websockets
from websockets.exceptions import ConnectionClosed

import config
from storage import data_store


class OnebotClient:
    """Onebot V11 WebSocket 客户端"""
    
    def __init__(self):
        self.ws_url = config.ONEBOT_WS_URL
        self.access_token = config.ONEBOT_ACCESS_TOKEN
        self.ws = None
        self._running = False
        self._message_handler: Optional[Callable] = None
        self._echo_handlers = {}
        self._echo_counter = 0

    def set_message_handler(self, handler: Callable[[dict], Awaitable[None]]):
        """设置消息处理器"""
        self._message_handler = handler

    async def connect(self):
        """连接到 Onebot 服务器"""
        try:
            headers = {}
            if self.access_token:
                headers['Authorization'] = f'Bearer {self.access_token}'
            
            self.ws = await websockets.connect(
                self.ws_url,
                additional_headers=headers if headers else None,
                ping_interval=config.ONEBOT_WS_PING_INTERVAL,
                ping_timeout=config.ONEBOT_WS_PING_TIMEOUT
            )
            print(f"已连接到 Onebot: {self.ws_url}")
            return True
        except Exception as e:
            print(f"连接 Onebot 失败: {e}")
            return False

    async def disconnect(self):
        """断开连接"""
        self._running = False
        if self.ws:
            await self.ws.close()

    async def send_api(self, action: str, params: dict = None, echo: str = None) -> Optional[dict]:
        """
        发送 API 请求
        
        Args:
            action: API 动作名
            params: 参数
            echo: 回显标识
            
        Returns:
            API 响应
        """
        if not self.ws:
            print("WebSocket 未连接")
            return None
        
        self._echo_counter += 1
        echo = echo or f"echo_{self._echo_counter}"
        
        message = {
            'action': action,
            'params': params or {},
            'echo': echo
        }
        
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self._echo_handlers[echo] = future
        
        try:
            await self.ws.send(json.dumps(message))
            # 等待响应，超时 10 秒
            result = await asyncio.wait_for(future, timeout=10)
            return result
        except asyncio.TimeoutError:
            print(f"API 请求超时: {action}")
            return None
        except Exception as e:
            print(f"API 请求失败: {e}")
            return None
        finally:
            self._echo_handlers.pop(echo, None)

    async def send_private_msg(self, user_id: int, message: str) -> Optional[dict]:
        """发送私聊消息"""
        print(f"[发送] 私聊 -> {user_id}: {message}")
        return await self.send_api('send_private_msg', {
            'user_id': user_id,
            'message': message
        })

    async def send_group_msg(self, group_id: int, message: str) -> Optional[dict]:
        """发送群消息"""
        print(f"[发送] 群聊 -> {group_id}: {message}")
        return await self.send_api('send_group_msg', {
            'group_id': group_id,
            'message': message
        })

    async def send_msg(self, message_type: str, target_id: int, message: str) -> Optional[dict]:
        """
        发送消息
        
        Args:
            message_type: 'private' 或 'group'
            target_id: 用户ID或群ID
            message: 消息内容
        """
        if message_type == 'private':
            return await self.send_private_msg(target_id, message)
        elif message_type == 'group':
            return await self.send_group_msg(target_id, message)
        return None

    async def _handle_message(self, data: dict):
        """处理收到的消息"""
        # 处理 API 响应
        echo = data.get('echo')
        if echo and echo in self._echo_handlers:
            self._echo_handlers[echo].set_result(data)
            return
        
        # 处理事件
        post_type = data.get('post_type')
        if post_type == 'message':
            # 输出收到的消息日志
            message_type = data.get('message_type')
            user_id = data.get('user_id')
            group_id = data.get('group_id')
            raw_message = data.get('raw_message', '')
            
            if message_type == 'private':
                print(f"[收到] 私聊 <- {user_id}: {raw_message}")
            elif message_type == 'group':
                print(f"[收到] 群聊 <- {group_id}/{user_id}: {raw_message}")
            
            if self._message_handler:
                await self._message_handler(data)

    async def run(self):
        """运行客户端主循环"""
        self._running = True
        
        while self._running:
            if not self.ws or self.ws.state.name != "OPEN":
                success = await self.connect()
                if not success:
                    await asyncio.sleep(5)  # 重连间隔
                    continue
            
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                await self._handle_message(data)
            except ConnectionClosed:
                print("WebSocket 连接已关闭，尝试重连...")
                self.ws = None
                await asyncio.sleep(5)
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
            except Exception as e:
                print(f"处理消息时发生错误: {e}")


class BotHandler:
    """机器人消息处理器"""
    
    # 绑定命令正则: /bind [username]
    BIND_PATTERN = re.compile(r'^/bind(?:\s+(\S+))?$')
    # 解绑命令
    UNBIND_PATTERN = re.compile(r'^/unbind$')
    # 查询绑定状态
    STATUS_PATTERN = re.compile(r'^/status$')
    
    def __init__(self, bot: OnebotClient):
        self.bot = bot
        self.bot.set_message_handler(self.handle_message)

    async def handle_message(self, event: dict):
        """处理消息事件"""
        message_type = event.get('message_type')
        raw_message = event.get('raw_message', '').strip()
        user_id = event.get('user_id')
        group_id = event.get('group_id')
        
        # 确定回复目标
        target_id = group_id if message_type == 'group' else user_id
        
        # 处理绑定命令
        bind_match = self.BIND_PATTERN.match(raw_message)
        if bind_match:
            username = bind_match.group(1)
            await self.handle_bind(message_type, target_id, user_id, username)
            return
        
        # 处理解绑命令
        if self.UNBIND_PATTERN.match(raw_message):
            await self.handle_unbind(message_type, target_id, user_id)
            return
        
        # 处理状态查询命令
        if self.STATUS_PATTERN.match(raw_message):
            await self.handle_status(message_type, target_id, user_id)
            return

    async def handle_bind(self, message_type: str, target_id: int, user_id: int, username: Optional[str] = None):
        """处理绑定请求"""
        qq_id = str(user_id)
        
        # 检查是否已绑定
        existing = data_store.get_binding(qq_id)
        if existing:
            await self.bot.send_msg(
                message_type, target_id,
                f"您已绑定账号: {existing.username}\n如需重新绑定，请先使用 /unbind 解绑"
            )
            return
        
        # 创建绑定会话
        session = data_store.create_bind_session(qq_id, username)
        
        # 生成绑定链接
        bind_url = f"{config.BASE_URL}/bind/{session.bind_code}"
        
        msg = f"请点击以下链接完成绑定验证:\n{bind_url}\n\n" \
              f"链接将在 {config.BIND_LINK_EXPIRE_SECONDS // 60} 分钟后过期"
        
        if username:
            msg += f"\n期望绑定的用户名: {username}"
        else:
            msg += "\n将绑定到登录的账号"

        await self.bot.send_msg(
            message_type, target_id,
            msg
        )

    async def handle_unbind(self, message_type: str, target_id: int, user_id: int):
        """处理解绑请求"""
        qq_id = str(user_id)
        
        existing = data_store.get_binding(qq_id)
        if not existing:
            await self.bot.send_msg(
                message_type, target_id,
                "您尚未绑定任何账号"
            )
            return
        
        username = existing.username
        data_store.remove_binding(qq_id)
        
        await self.bot.send_msg(
            message_type, target_id,
            f"已成功解绑账号: {username}"
        )

    async def handle_status(self, message_type: str, target_id: int, user_id: int):
        """处理状态查询"""
        qq_id = str(user_id)
        
        existing = data_store.get_binding(qq_id)
        if existing:
            from datetime import datetime
            bound_time = datetime.fromtimestamp(existing.bound_at).strftime('%Y-%m-%d %H:%M:%S')
            await self.bot.send_msg(
                message_type, target_id,
                f"当前绑定状态:\n"
                f"用户名: {existing.username}\n"
                f"绑定时间: {bound_time}"
            )
        else:
            await self.bot.send_msg(
                message_type, target_id,
                "您尚未绑定任何账号\n使用 /bind <用户名> 开始绑定"
            )


# 全局机器人实例
bot_client = OnebotClient()
bot_handler = BotHandler(bot_client)
