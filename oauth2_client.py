"""
OAuth2 客户端模块
处理与 SSO 服务器的 OAuth2 交互
"""
import httpx
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import config


class OAuth2Client:
    """OAuth2 客户端"""
    
    def __init__(self):
        self.client_id = config.OAUTH2_CLIENT_ID
        self.client_secret = config.OAUTH2_CLIENT_SECRET
        self.authorize_url = config.OAUTH2_AUTHORIZE_URL
        self.token_url = config.OAUTH2_TOKEN_URL
        self.userinfo_url = config.OAUTH2_USERINFO_URL
        self.redirect_uri = config.OAUTH2_REDIRECT_URI
        self.scope = config.OAUTH2_SCOPE

    def get_authorization_url(self, state: str) -> str:
        """
        生成授权 URL
        
        Args:
            state: OAuth2 state 参数，用于防止 CSRF 攻击
            
        Returns:
            完整的授权 URL
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'state': state
        }
        return f"{self.authorize_url}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        用授权码换取访问令牌
        
        Args:
            code: 授权码
            
        Returns:
            (token_data, error_msg) - 成功返回 (dict, None)，失败返回 (None, error_msg)
        """
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        if config.DEBUG:
            print(f"[DEBUG] Token请求 URL: {self.token_url}")
            print(f"[DEBUG] Token请求参数: client_id={self.client_id}, redirect_uri={self.redirect_uri}")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                if config.DEBUG:
                    print(f"[DEBUG] Token响应状态码: {response.status_code}")
                    print(f"[DEBUG] Token响应内容: {response.text}")
                
                if response.status_code == 200:
                    return response.json(), None
                else:
                    error_msg = f"获取token失败: {response.status_code} - {response.text}"
                    print(error_msg)
                    return None, error_msg
        except Exception as e:
            error_msg = f"请求token时发生错误: {e}"
            print(error_msg)
            return None, error_msg

    async def get_user_info(self, access_token: str) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        获取用户信息
        
        Args:
            access_token: 访问令牌
            
        Returns:
            (user_info, error_msg) - 成功返回 (dict, None)，失败返回 (None, error_msg)
        """
        if config.DEBUG:
            print(f"[DEBUG] UserInfo请求 URL: {self.userinfo_url}")
        
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(
                    self.userinfo_url,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                
                if config.DEBUG:
                    print(f"[DEBUG] UserInfo响应状态码: {response.status_code}")
                    print(f"[DEBUG] UserInfo响应内容: {response.text}")
                
                if response.status_code == 200:
                    return response.json(), None
                else:
                    error_msg = f"获取用户信息失败: {response.status_code} - {response.text}"
                    if response.status_code == 403:
                        error_msg += "\n[提示] 403 Forbidden 通常意味着权限不足。请检查 .env 中的 OAUTH2_SCOPE 是否包含 'openid' 和 'profile'。"
                    print(error_msg)
                    return None, error_msg
        except Exception as e:
            error_msg = f"请求用户信息时发生错误: {e}"
            print(error_msg)
            return None, error_msg

    async def get_username_from_code(self, code: str) -> tuple[Optional[str], Optional[str]]:
        """
        从授权码获取用户名
        
        Args:
            code: 授权码
            
        Returns:
            (username, error_msg) - 成功返回 (str, None)，失败返回 (None, error_msg)
        """
        # 1. 换取 token
        token_data, error = await self.exchange_code_for_token(code)
        if not token_data:
            return None, error or "获取token失败"
        
        access_token = token_data.get('access_token')
        if not access_token:
            error_msg = f"Token响应中没有access_token，响应内容: {token_data}"
            print(error_msg)
            return None, error_msg
        
        # 2. 获取用户信息
        user_info, error = await self.get_user_info(access_token)
        if not user_info:
            return None, error or "获取用户信息失败"
        
        if config.DEBUG:
            print(f"[DEBUG] 完整用户信息: {user_info}")
        
        # 尝试从不同的字段获取用户名
        # 不同的 SSO 服务器可能使用不同的字段名
        username = (
            user_info.get('preferred_username') or
            user_info.get('username') or
            user_info.get('name') or
            user_info.get('sub')
        )
        
        if not username:
            error_msg = f"无法从用户信息中提取用户名，用户信息: {user_info}"
            print(error_msg)
            return None, error_msg
        
        return username, None


# 全局 OAuth2 客户端实例
oauth2_client = OAuth2Client()
