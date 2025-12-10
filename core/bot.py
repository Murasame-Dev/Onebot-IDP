"""
机器人消息处理器
处理绑定命令和用户交互
"""
import re
from typing import Optional, Union

import config
from text import text
from core.storage import data_store
from core.onebot import OnebotClient, OnebotServer, bot_client


class BotHandler:
    """机器人消息处理器"""
    
    def __init__(self, bot: Union[OnebotClient, OnebotServer]):
        self.bot = bot
        self.bot.set_message_handler(self.handle_message)
        # 动态构建命令正则
        self._build_patterns()
    
    def _build_patterns(self):
        """根据配置构建命令正则表达式"""
        prefix = re.escape(config.CMD_PREFIX)
        # 绑定命令正则: /bind [username]
        self.BIND_PATTERN = re.compile(rf'^{prefix}{config.CMD_BIND}(?:\s+(\S+))?$')
        # 取消绑定请求命令
        self.BIND_CANCEL_PATTERN = re.compile(rf'^{prefix}{config.CMD_BIND_CANCEL}$')
        # 解绑命令
        self.UNBIND_PATTERN = re.compile(rf'^{prefix}{config.CMD_UNBIND}$')
        # 查询绑定状态
        self.STATUS_PATTERN = re.compile(rf'^{prefix}{config.CMD_STATUS}$')
        # 登录命令: /login 验证码
        self.LOGIN_PATTERN = re.compile(rf'^{prefix}{config.CMD_LOGIN}\s+(\d{{6}})$')

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
            # /bind 不带用户名只支持私聊，/bind xxx 支持所有环境
            if not username and message_type != 'private':
                await self.bot.send_msg(message_type, target_id, text.BIND_PRIVATE_ONLY)
                return
            await self.handle_bind(message_type, target_id, user_id, username)
            return
        
        # 处理取消绑定请求命令
        if self.BIND_CANCEL_PATTERN.match(raw_message):
            await self.handle_bind_cancel(message_type, target_id, user_id)
            return
        
        # 处理解绑命令
        if self.UNBIND_PATTERN.match(raw_message):
            await self.handle_unbind(message_type, target_id, user_id)
            return
        
        # 处理状态查询命令
        if self.STATUS_PATTERN.match(raw_message):
            await self.handle_status(message_type, target_id, user_id)
            return

        # 处理登录授权命令
        login_match = self.LOGIN_PATTERN.match(raw_message)
        if login_match:
            login_code = login_match.group(1)
            await self.handle_login(message_type, target_id, user_id, login_code)
            return

    async def handle_bind(self, message_type: str, target_id: int, user_id: int, username: Optional[str] = None):
        """处理绑定请求"""
        uin = str(user_id)
        
        # 检查是否已绑定
        existing = data_store.get_binding(uin)
        if existing:
            await self.bot.send_msg(
                message_type, target_id,
                text.BIND_ALREADY_BOUND.format(username=existing.username)
            )
            return
        
        # 检查是否有进行中的绑定请求
        existing_session = data_store.get_session_by_uin(uin)
        if existing_session:
            await self.bot.send_msg(message_type, target_id, text.BIND_REQUEST_EXISTS)
            return
        
        # 创建绑定会话
        session = data_store.create_bind_session(uin, username)
        
        # 生成绑定链接
        bind_url = f"{config.BASE_URL}/bind/{session.bind_code}"
        expire_minutes = config.BIND_LINK_EXPIRE_SECONDS // 60
        
        msg = text.BIND_LINK_MESSAGE.format(bind_url=bind_url, expire_minutes=expire_minutes)
        
        if username:
            msg += text.BIND_LINK_EXPECTED_USER.format(username=username)
        else:
            msg += text.BIND_LINK_ANY_USER

        await self.bot.send_msg(message_type, target_id, msg)

    async def handle_bind_cancel(self, message_type: str, target_id: int, user_id: int):
        """处理取消绑定请求"""
        uin = str(user_id)
        
        if data_store.cancel_bind_session_by_uin(uin):
            await self.bot.send_msg(message_type, target_id, text.BIND_CANCEL_SUCCESS)
        else:
            await self.bot.send_msg(message_type, target_id, text.BIND_CANCEL_NO_REQUEST)

    async def handle_unbind(self, message_type: str, target_id: int, user_id: int):
        """处理解绑请求"""
        uin = str(user_id)
        
        existing = data_store.get_binding(uin)
        if not existing:
            await self.bot.send_msg(message_type, target_id, text.UNBIND_NOT_BOUND)
            return
        
        username = existing.username
        data_store.remove_binding(uin)
        
        await self.bot.send_msg(
            message_type, target_id,
            text.UNBIND_SUCCESS.format(username=username)
        )

    async def handle_status(self, message_type: str, target_id: int, user_id: int):
        """处理状态查询"""
        uin = str(user_id)
        
        existing = data_store.get_binding(uin)
        if existing:
            from datetime import datetime
            bound_time = datetime.fromtimestamp(existing.bound_at).strftime('%Y-%m-%d %H:%M:%S')
            await self.bot.send_msg(
                message_type, target_id,
                text.STATUS_BOUND.format(username=existing.username, bound_time=bound_time)
            )
        else:
            await self.bot.send_msg(message_type, target_id, text.STATUS_NOT_BOUND)

    async def handle_login(self, message_type: str, target_id: int, user_id: int, login_code: str):
        """处理登录授权请求"""
        uin = str(user_id)
        
        # 检查用户是否已绑定
        binding = data_store.get_binding(uin)
        if not binding:
            await self.bot.send_msg(message_type, target_id, text.LOGIN_NOT_BOUND)
            return
        
        # 获取登录会话
        session = data_store.get_login_session(login_code)
        if not session:
            await self.bot.send_msg(message_type, target_id, text.LOGIN_CODE_INVALID)
            return
        
        # 授权登录
        auth_code = data_store.authorize_login_session(login_code, uin)
        if not auth_code:
            await self.bot.send_msg(message_type, target_id, text.LOGIN_AUTH_FAILED)
            return
        
        await self.bot.send_msg(
            message_type, target_id,
            text.LOGIN_AUTH_SUCCESS.format(username=binding.username)
        )


# 全局处理器实例
bot_handler = BotHandler(bot_client)
