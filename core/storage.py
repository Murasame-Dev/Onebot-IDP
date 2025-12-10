"""
数据存储模块
管理用户绑定信息和临时绑定会话
"""
import json
import os
import time
import secrets
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from threading import Lock

import config


@dataclass
class BindingSession:
    """绑定会话"""
    bind_code: str  # 随机生成的绑定码
    uin: str  # QQ号
    expected_username: Optional[str]  # 期望绑定的用户名
    created_at: float  # 创建时间戳
    state: str  # OAuth2 state 参数

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return time.time() - self.created_at > config.BIND_LINK_EXPIRE_SECONDS


@dataclass
class LoginSession:
    """OAuth2 登录会话（IDP 模式）"""
    login_code: str  # 6位数字验证码
    client_id: str  # 请求授权的应用 client_id
    redirect_uri: str  # 回调地址
    state: str  # 应用传入的 state
    scope: str  # 请求的权限范围
    created_at: float  # 创建时间戳
    uin: Optional[str] = None  # 完成验证后的 QQ 号
    authorized: bool = False  # 是否已授权
    auth_code: Optional[str] = None  # 授权码（用户授权后生成）

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return time.time() - self.created_at > config.LOGIN_CODE_EXPIRE_SECONDS


@dataclass
class UserBinding:
    """用户绑定信息"""
    uin: str
    username: str
    bound_at: float  # 绑定时间戳
    extra_fields: Optional[Dict[str, Any]] = None  # 额外记录的用户信息字段


class DataStore:
    """数据存储类"""
    
    def __init__(self):
        self._lock = Lock()
        self._bindings: Dict[str, UserBinding] = {}  # QQ号 -> 绑定信息
        self._sessions: Dict[str, BindingSession] = {}  # bind_code -> 会话信息
        self._state_to_code: Dict[str, str] = {}  # state -> bind_code 映射
        self._uin_to_code: Dict[str, str] = {}  # uin -> bind_code 映射（确保每用户只有一个请求）
        self._login_sessions: Dict[str, LoginSession] = {}  # login_code -> 登录会话
        self._auth_codes: Dict[str, LoginSession] = {}  # auth_code -> 已授权的登录会话
        self._authorized_logins: Dict[str, LoginSession] = {}  # login_code -> 已授权的会话(用于前端查询)
        self._load_bindings()

    def _load_bindings(self):
        """从文件加载绑定数据"""
        if os.path.exists(config.DATA_FILE):
            try:
                with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for uin, info in data.items():
                        # 基础字段
                        base_fields = {'uin', 'username', 'bound_at'}
                        # 提取额外字段（非基础字段都是额外字段）
                        extra_fields = {k: v for k, v in info.items() if k not in base_fields}
                        
                        self._bindings[uin] = UserBinding(
                            uin=info['uin'],
                            username=info['username'],
                            bound_at=info['bound_at'],
                            extra_fields=extra_fields if extra_fields else None
                        )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"加载绑定数据失败: {e}")
                self._bindings = {}

    def _save_bindings(self):
        """保存绑定数据到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
        with open(config.DATA_FILE, 'w', encoding='utf-8') as f:
            data = {}
            for uin, binding in self._bindings.items():
                binding_dict = {
                    'uin': binding.uin,
                    'username': binding.username,
                    'bound_at': binding.bound_at
                }
                # 展开 extra_fields 到顶层
                if binding.extra_fields:
                    binding_dict.update(binding.extra_fields)
                data[uin] = binding_dict
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_session_by_uin(self, uin: str) -> Optional[BindingSession]:
        """通过QQ号获取会话（检查是否有进行中的绑定请求）"""
        with self._lock:
            bind_code = self._uin_to_code.get(uin)
            if bind_code:
                session = self._sessions.get(bind_code)
                if session and not session.is_expired():
                    return session
                elif session:
                    # 清理过期会话
                    self._cleanup_session(bind_code)
            return None

    def cancel_bind_session_by_uin(self, uin: str) -> bool:
        """通过QQ号取消绑定会话"""
        with self._lock:
            bind_code = self._uin_to_code.get(uin)
            if bind_code:
                self._cleanup_session(bind_code)
                return True
            return False

    def create_bind_session(self, uin: str, expected_username: Optional[str]) -> BindingSession:
        """创建绑定会话"""
        with self._lock:
            # 清理该用户可能存在的旧会话
            old_code = self._uin_to_code.get(uin)
            if old_code:
                self._cleanup_session(old_code)
            
            # 生成随机绑定码和state
            bind_code = secrets.token_urlsafe(16)
            state = secrets.token_urlsafe(32)
            
            session = BindingSession(
                bind_code=bind_code,
                uin=uin,
                expected_username=expected_username,
                created_at=time.time(),
                state=state
            )
            
            self._sessions[bind_code] = session
            self._state_to_code[state] = bind_code
            self._uin_to_code[uin] = bind_code
            
            return session

    def get_session_by_code(self, bind_code: str) -> Optional[BindingSession]:
        """通过绑定码获取会话"""
        with self._lock:
            session = self._sessions.get(bind_code)
            if session and not session.is_expired():
                return session
            elif session:
                # 清理过期会话
                self._cleanup_session(bind_code)
            return None

    def get_session_by_state(self, state: str) -> Optional[BindingSession]:
        """通过state获取会话"""
        with self._lock:
            bind_code = self._state_to_code.get(state)
            if bind_code:
                session = self._sessions.get(bind_code)
                if session and not session.is_expired():
                    return session
                elif session:
                    self._cleanup_session(bind_code)
            return None

    def _cleanup_session(self, bind_code: str):
        """清理会话"""
        session = self._sessions.pop(bind_code, None)
        if session:
            self._state_to_code.pop(session.state, None)
            self._uin_to_code.pop(session.uin, None)

    def remove_session(self, bind_code: str):
        """移除会话"""
        with self._lock:
            self._cleanup_session(bind_code)

    def add_binding(self, uin: str, username: str, extra_fields: Optional[Dict[str, Any]] = None) -> UserBinding:
        """添加用户绑定"""
        with self._lock:
            binding = UserBinding(
                uin=uin,
                username=username,
                bound_at=time.time(),
                extra_fields=extra_fields
            )
            self._bindings[uin] = binding
            self._save_bindings()
            return binding

    def get_binding(self, uin: str) -> Optional[UserBinding]:
        """获取用户绑定信息"""
        with self._lock:
            return self._bindings.get(uin)

    def remove_binding(self, uin: str) -> bool:
        """移除用户绑定"""
        with self._lock:
            if uin in self._bindings:
                del self._bindings[uin]
                self._save_bindings()
                return True
            return False

    def get_all_bindings(self) -> Dict[str, UserBinding]:
        """获取所有绑定信息"""
        with self._lock:
            return dict(self._bindings)

    # ===== OAuth2 IDP 登录会话管理 =====

    def create_login_session(self, client_id: str, redirect_uri: str, state: str, scope: str) -> LoginSession:
        """创建登录会话，返回包含验证码的会话"""
        with self._lock:
            # 生成6位数字验证码
            login_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # 确保验证码唯一
            while login_code in self._login_sessions:
                login_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            session = LoginSession(
                login_code=login_code,
                client_id=client_id,
                redirect_uri=redirect_uri,
                state=state,
                scope=scope,
                created_at=time.time()
            )
            
            self._login_sessions[login_code] = session
            return session

    def get_login_session(self, login_code: str) -> Optional[LoginSession]:
        """通过验证码获取登录会话"""
        with self._lock:
            session = self._login_sessions.get(login_code)
            if session and not session.is_expired():
                return session
            elif session:
                # 清理过期会话
                del self._login_sessions[login_code]
            return None

    def authorize_login_session(self, login_code: str, uin: str) -> Optional[str]:
        """
        授权登录会话（用户输入验证码后调用）
        返回授权码，如果失败返回 None
        """
        with self._lock:
            session = self._login_sessions.get(login_code)
            if not session or session.is_expired():
                return None
            
            # 生成授权码
            auth_code = secrets.token_urlsafe(32)
            
            # 更新会话状态
            session.uin = uin
            session.authorized = True
            session.auth_code = auth_code
            
            # 将授权码映射到会话
            self._auth_codes[auth_code] = session
            
            # 保存到已授权列表（供前端查询）
            self._authorized_logins[login_code] = session
            
            # 从待验证列表移除
            del self._login_sessions[login_code]
            
            return auth_code

    def get_authorized_login(self, login_code: str) -> Optional[LoginSession]:
        """获取已授权的登录会话（供前端轮询）"""
        with self._lock:
            return self._authorized_logins.get(login_code)

    def remove_authorized_login(self, login_code: str):
        """移除已授权的登录记录"""
        with self._lock:
            self._authorized_logins.pop(login_code, None)

    def get_session_by_auth_code(self, auth_code: str) -> Optional[LoginSession]:
        """通过授权码获取会话（用于 token 交换）"""
        with self._lock:
            session = self._auth_codes.get(auth_code)
            if session and not session.is_expired():
                return session
            elif session:
                del self._auth_codes[auth_code]
            return None

    def consume_auth_code(self, auth_code: str) -> Optional[LoginSession]:
        """消费授权码，返回会话并删除"""
        with self._lock:
            session = self._auth_codes.pop(auth_code, None)
            if session and not session.is_expired():
                return session
            return None

    def cleanup_expired_login_sessions(self):
        """清理过期的登录会话"""
        with self._lock:
            expired_codes = [
                code for code, session in self._login_sessions.items()
                if session.is_expired()
            ]
            for code in expired_codes:
                del self._login_sessions[code]
            
            expired_auth_codes = [
                code for code, session in self._auth_codes.items()
                if session.is_expired()
            ]
            for code in expired_auth_codes:
                del self._auth_codes[code]


# 全局数据存储实例
data_store = DataStore()
