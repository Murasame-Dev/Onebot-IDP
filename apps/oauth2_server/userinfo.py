"""
/oauth/userinfo 端点
返回用户信息
"""
import base64
import json
from fastapi import APIRouter, HTTPException, Request

import config
from core.storage import data_store

router = APIRouter()


@router.get("/userinfo")
async def oauth_userinfo(request: Request):
    """
    OAuth2 UserInfo 端点
    返回当前用户信息，输出字段由 IDP_USERINFO_OUTPUT_FIELDS 配置
    """
    if not config.IDP_ENABLED:
        raise HTTPException(status_code=403, detail="IDP 功能未启用")
    
    # 从 Authorization header 获取 token
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少或无效的 Authorization header")
    
    token = auth_header[7:]  # 去掉 "Bearer " 前缀
    
    try:
        token_data = json.loads(base64.urlsafe_b64decode(token).decode())
        
        # 获取用户绑定信息（包含额外字段）
        binding = data_store.get_binding(token_data["uin"])
        
        # 可用的所有字段
        all_fields = {
            "sub": token_data["uin"],
            "preferred_username": token_data["username"],
            "username": token_data["username"],
            "uin": token_data["uin"]
        }
        
        # 添加绑定时保存的额外字段
        if binding and binding.extra_fields:
            all_fields.update(binding.extra_fields)
        
        # 根据配置过滤输出字段
        output_fields = config.IDP_USERINFO_OUTPUT_FIELDS
        if output_fields:
            result = {k: v for k, v in all_fields.items() if k in output_fields}
        else:
            result = all_fields
        
        if config.DEBUG:
            print(f"[DEBUG] UserInfo 输出: {result}")
        
        return result
    except Exception as e:
        if config.DEBUG:
            print(f"[DEBUG] UserInfo 错误: {e}")
        raise HTTPException(status_code=401, detail="无效的 access_token")
