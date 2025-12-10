"""
/oauth/token 端点
用授权码交换 access_token
"""
import base64
import json
from fastapi import APIRouter, HTTPException, Request

import config
from core.storage import data_store

router = APIRouter()


@router.post("/token")
async def oauth_token(request: Request):
    """
    OAuth2 Token 端点
    用授权码交换 access_token
    支持 form-urlencoded 和 Basic Auth
    """
    if not config.IDP_ENABLED:
        raise HTTPException(status_code=403, detail="IDP 功能未启用")
    
    # 从 form data 获取参数
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    code = form_data.get("code")
    redirect_uri = form_data.get("redirect_uri")
    client_id = form_data.get("client_id")
    client_secret = form_data.get("client_secret")
    
    # 尝试从 Basic Auth 获取 client 凭证
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Basic "):
        try:
            credentials = base64.b64decode(auth_header[6:]).decode()
            if ":" in credentials:
                basic_client_id, basic_client_secret = credentials.split(":", 1)
                if not client_id:
                    client_id = basic_client_id
                if not client_secret:
                    client_secret = basic_client_secret
        except Exception:
            pass
    
    if config.DEBUG:
        print(f"[DEBUG] Token 请求: grant_type={grant_type}, code={code[:20] if code else None}..., client_id={client_id}")
    
    # 验证 grant_type
    if grant_type != "authorization_code":
        raise HTTPException(status_code=400, detail=f"仅支持 grant_type=authorization_code, 收到: {grant_type}")
    
    # 验证 client 凭证
    if client_id != config.IDP_CLIENT_ID or client_secret != config.IDP_CLIENT_SECRET:
        if config.DEBUG:
            print(f"[DEBUG] Client 验证失败: 期望 client_id={config.IDP_CLIENT_ID}, 收到 {client_id}")
        raise HTTPException(status_code=401, detail="无效的客户端凭证")
    
    # 验证授权码
    if not code:
        raise HTTPException(status_code=400, detail="缺少授权码")
    
    # 消费授权码获取会话
    session = data_store.consume_auth_code(code)
    if not session:
        raise HTTPException(status_code=400, detail="无效或过期的授权码")
    
    # 验证 redirect_uri
    if redirect_uri and redirect_uri != session.redirect_uri:
        raise HTTPException(status_code=400, detail="redirect_uri 不匹配")
    
    # 获取用户绑定信息
    binding = data_store.get_binding(session.uin)
    if not binding:
        raise HTTPException(status_code=500, detail="用户绑定信息不存在")
    
    # 生成 access_token
    token_data = {
        "uin": session.uin,
        "username": binding.username,
        "scope": session.scope
    }
    access_token = base64.urlsafe_b64encode(
        json.dumps(token_data).encode()
    ).decode()
    
    if config.DEBUG:
        print(f"[DEBUG] Token 生成成功: uin={session.uin}, username={binding.username}")
    
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": session.scope
    }
