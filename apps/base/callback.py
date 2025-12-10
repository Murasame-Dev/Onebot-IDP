"""
/callback 端点
OAuth2 回调处理
"""
import asyncio
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

import config
from text import text
from core.storage import data_store
from core.oauth2_client import oauth2_client
from core.onebot import bot_client
from .templates import SUCCESS_HTML, ERROR_HTML

router = APIRouter(tags=["绑定"])


async def notify_user(user_id: int, message: str):
    """后台发送通知给用户"""
    try:
        await bot_client.send_private_msg(user_id, message)
    except Exception as e:
        print(f"发送通知失败: {e}")


@router.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """
    OAuth2 回调处理
    SSO 服务器授权后会重定向到这里
    """
    # 处理授权错误
    if error:
        return HTMLResponse(
            ERROR_HTML.format(error=f"授权失败: {error}"),
            status_code=400
        )
    
    # 验证参数
    if not code or not state:
        return HTMLResponse(
            ERROR_HTML.format(error="缺少必要参数"),
            status_code=400
        )
    
    # 通过 state 获取会话
    session = data_store.get_session_by_state(state)
    if not session:
        return HTMLResponse(
            ERROR_HTML.format(error="会话无效或已过期，请重新发起绑定请求"),
            status_code=400
        )
    
    # 使用授权码获取用户名和用户信息
    actual_username, error_msg, user_info = await oauth2_client.get_username_from_code(code)
    if not actual_username:
        display_error = f"获取用户信息失败: {error_msg}" if error_msg else "获取用户信息失败，请重试"
        return HTMLResponse(
            ERROR_HTML.format(error=display_error),
            status_code=500
        )
    
    # 验证用户名是否匹配
    if session.expected_username and actual_username.lower() != session.expected_username.lower():
        error_msg = (
            f"用户名不匹配！\n"
            f"期望: {session.expected_username}\n"
            f"实际: {actual_username}\n"
            f"请确认您使用正确的账号登录"
        )
        
        # 清理会话
        data_store.remove_session(session.bind_code)
        
        # 后台发送通知
        asyncio.create_task(notify_user(
            int(session.uin),
            text.NOTIFY_BIND_USERNAME_MISMATCH.format(
                expected=session.expected_username,
                actual=actual_username
            )
        ))
        
        return HTMLResponse(
            ERROR_HTML.format(error=error_msg.replace('\n', '<br>')),
            status_code=400
        )
    
    # 提取配置中指定的额外字段
    extra_fields = None
    if config.BIND_RECORD_FIELDS and user_info:
        extra_fields = {}
        for field in config.BIND_RECORD_FIELDS:
            if field in user_info:
                extra_fields[field] = user_info[field]
        if not extra_fields:
            extra_fields = None
    
    # 绑定成功
    data_store.add_binding(session.uin, actual_username, extra_fields)
    
    # 清理会话
    data_store.remove_session(session.bind_code)
    
    # 后台发送通知
    asyncio.create_task(notify_user(
        int(session.uin),
        text.NOTIFY_BIND_SUCCESS.format(username=actual_username)
    ))
    
    return HTMLResponse(SUCCESS_HTML.format(username=actual_username))
