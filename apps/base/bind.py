"""
/bind 端点
绑定页面入口
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from core.storage import data_store
from core.oauth2_client import oauth2_client
from .templates import ERROR_HTML

router = APIRouter(tags=["绑定"])


@router.get("/bind/{bind_code}")
async def bind_page(bind_code: str):
    """
    绑定页面 - 用户点击绑定链接后的入口
    重定向到 OAuth2 授权页面
    """
    # 检查会话是否存在且有效
    session = data_store.get_session_by_code(bind_code)
    if not session:
        return HTMLResponse(
            ERROR_HTML.format(error="绑定链接无效或已过期，请重新发起绑定请求"),
            status_code=400
        )
    
    # 生成 OAuth2 授权 URL 并重定向
    auth_url = oauth2_client.get_authorization_url(session.state)
    return RedirectResponse(url=auth_url)
