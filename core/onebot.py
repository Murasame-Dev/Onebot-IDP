"""
Onebot V11 WebSocket 客户端/服务端
支持两种模式:
- client: 主动连接到 Onebot 实现
- server: 等待 Onebot 实现连接
"""
import asyncio
import json
from typing import Optional, Callable, Awaitable, Set

import websockets
from websockets.exceptions import ConnectionClosed
from websockets.server import serve

import config


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
                # 异步处理消息，不阻塞主循环
                asyncio.create_task(self._message_handler(data))

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


class OnebotServer:
    """Onebot V11 WebSocket 服务端，等待 Onebot 客户端连接"""
    
    def __init__(self):
        self.host = config.ONEBOT_WS_HOST
        self.port = config.ONEBOT_WS_PORT
        self.access_token = config.ONEBOT_ACCESS_TOKEN
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.ws = None  # 当前活跃的连接（用于发送消息）
        self._running = False
        self._message_handler: Optional[Callable] = None
        self._echo_handlers = {}
        self._echo_counter = 0

    def set_message_handler(self, handler: Callable[[dict], Awaitable[None]]):
        """设置消息处理器"""
        self._message_handler = handler

    async def _verify_token(self, websocket) -> bool:
        """验证访问令牌"""
        if not self.access_token:
            return True
        
        # 从请求头获取 token
        auth_header = websocket.request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            return token == self.access_token
        
        # 也支持从查询参数获取
        # ws://host:port/?access_token=xxx
        path = websocket.request.path
        if 'access_token=' in path:
            import urllib.parse
            parsed = urllib.parse.urlparse(path)
            params = urllib.parse.parse_qs(parsed.query)
            token = params.get('access_token', [''])[0]
            return token == self.access_token
        
        return False

    async def _handle_client(self, websocket):
        """处理客户端连接"""
        # 验证 token
        if not await self._verify_token(websocket):
            print(f"客户端连接被拒绝: Token 验证失败")
            await websocket.close(1008, "Unauthorized")
            return
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"Onebot 客户端已连接: {client_info}")
        
        self.clients.add(websocket)
        self.ws = websocket  # 设置当前活跃连接
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError as e:
                    print(f"JSON 解析错误: {e}")
        except ConnectionClosed:
            print(f"Onebot 客户端断开连接: {client_info}")
        finally:
            self.clients.discard(websocket)
            if self.ws == websocket:
                # 如果还有其他连接，使用其中一个
                self.ws = next(iter(self.clients), None)

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
                # 异步处理消息，不阻塞主循环
                asyncio.create_task(self._message_handler(data))

    async def send_api(self, action: str, params: dict = None, echo: str = None) -> Optional[dict]:
        """发送 API 请求"""
        if not self.ws:
            print("没有活跃的 Onebot 连接")
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
        """发送消息"""
        if message_type == 'private':
            return await self.send_private_msg(target_id, message)
        elif message_type == 'group':
            return await self.send_group_msg(target_id, message)
        return None

    async def run(self):
        """运行服务端"""
        self._running = True
        print(f"启动 Onebot WebSocket 服务端: {self.host}:{self.port}")
        
        async with serve(
            self._handle_client,
            self.host,
            self.port,
            ping_interval=config.ONEBOT_WS_PING_INTERVAL,
            ping_timeout=config.ONEBOT_WS_PING_TIMEOUT
        ):
            print(f"等待 Onebot 客户端连接...")
            await asyncio.Future()  # 永久运行


def create_bot_instance():
    """根据配置创建机器人实例"""
    if config.ONEBOT_MODE.lower() == 'server':
        return OnebotServer()
    else:
        return OnebotClient()


# 全局机器人实例
bot_client = create_bot_instance()
