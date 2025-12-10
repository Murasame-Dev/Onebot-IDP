"""
/oauth/check_status 端点
检查授权状态（供前端轮询）
"""
from fastapi import APIRouter

from core.storage import data_store

router = APIRouter()


@router.get("/check_status")
async def oauth_check_status(login_code: str):
    """
    检查授权状态 (供前端轮询)
    """
    # 先检查是否还在等待中
    session = data_store.get_login_session(login_code)
    if session:
        # 会话存在但未授权
        return {"authorized": False, "status": "waiting"}
    
    # 检查是否已授权
    authorized_session = data_store.get_authorized_login(login_code)
    if authorized_session and authorized_session.authorized:
        # 构建回调 URL
        redirect_url = authorized_session.redirect_uri
        params = [f"code={authorized_session.auth_code}"]
        if authorized_session.state:
            params.append(f"state={authorized_session.state}")
        
        if "?" in redirect_url:
            redirect_url += "&" + "&".join(params)
        else:
            redirect_url += "?" + "&".join(params)
        
        # 清理已授权记录
        data_store.remove_authorized_login(login_code)
        
        return {
            "authorized": True,
            "status": "authorized",
            "redirect_url": redirect_url
        }
    
    # 会话不存在，可能已过期
    return {"authorized": False, "status": "expired", "message": "会话不存在或已过期"}


@router.post("/check_status")
async def oauth_check_status_post(login_code: str):
    """检查授权状态 (POST 方式)"""
    return await oauth_check_status(login_code)
