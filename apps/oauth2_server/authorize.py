"""
/oauth/authorize 端点
OAuth2 授权入口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

import config
from core.storage import data_store
from .templates import LOGIN_PAGE_HTML

router = APIRouter()


@router.get("/authorize")
async def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    scope: str = "openid profile",
    state: str = ""
):
    """
    OAuth2 授权端点 (IDP 模式)
    第三方应用重定向用户到此端点请求授权
    """
    if not config.IDP_ENABLED:
        raise HTTPException(status_code=403, detail="IDP 功能未启用")
    
    # 验证 response_type
    if response_type != "code":
        raise HTTPException(status_code=400, detail="仅支持 response_type=code")
    
    # 验证 client_id
    if client_id != config.IDP_CLIENT_ID:
        raise HTTPException(status_code=400, detail="无效的 client_id")
    
    # 验证 redirect_uri
    allowed_uris = [uri.strip() for uri in config.IDP_ALLOWED_REDIRECT_URIS if uri.strip()]
    if allowed_uris and redirect_uri not in allowed_uris:
        raise HTTPException(status_code=400, detail="redirect_uri 不在允许列表中")
    
    # 创建登录会话
    session = data_store.create_login_session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state,
        scope=scope
    )
    
    return HTMLResponse(
        LOGIN_PAGE_HTML.format(
            login_cmd=config.FULL_CMD_LOGIN,
            login_code=session.login_code,
            expire_seconds=config.LOGIN_CODE_EXPIRE_SECONDS
        )
    )
