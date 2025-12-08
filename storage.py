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
    qq_id: str  # QQ号
    expected_username: Optional[str]  # 期望绑定的用户名
    created_at: float  # 创建时间戳
    state: str  # OAuth2 state 参数

    def is_expired(self) -> bool:
        """检查会话是否过期"""
        return time.time() - self.created_at > config.BIND_LINK_EXPIRE_SECONDS


@dataclass
class UserBinding:
    """用户绑定信息"""
    qq_id: str
    username: str
    bound_at: float  # 绑定时间戳


class DataStore:
    """数据存储类"""
    
    def __init__(self):
        self._lock = Lock()
        self._bindings: Dict[str, UserBinding] = {}  # QQ号 -> 绑定信息
        self._sessions: Dict[str, BindingSession] = {}  # bind_code -> 会话信息
        self._state_to_code: Dict[str, str] = {}  # state -> bind_code 映射
        self._load_bindings()

    def _load_bindings(self):
        """从文件加载绑定数据"""
        if os.path.exists(config.DATA_FILE):
            try:
                with open(config.DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for qq_id, info in data.items():
                        self._bindings[qq_id] = UserBinding(
                            qq_id=info['qq_id'],
                            username=info['username'],
                            bound_at=info['bound_at']
                        )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"加载绑定数据失败: {e}")
                self._bindings = {}

    def _save_bindings(self):
        """保存绑定数据到文件"""
        with open(config.DATA_FILE, 'w', encoding='utf-8') as f:
            data = {qq_id: asdict(binding) for qq_id, binding in self._bindings.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_bind_session(self, qq_id: str, expected_username: Optional[str]) -> BindingSession:
        """创建绑定会话"""
        with self._lock:
            # 生成随机绑定码和state
            bind_code = secrets.token_urlsafe(16)
            state = secrets.token_urlsafe(32)
            
            session = BindingSession(
                bind_code=bind_code,
                qq_id=qq_id,
                expected_username=expected_username,
                created_at=time.time(),
                state=state
            )
            
            self._sessions[bind_code] = session
            self._state_to_code[state] = bind_code
            
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

    def remove_session(self, bind_code: str):
        """移除会话"""
        with self._lock:
            self._cleanup_session(bind_code)

    def add_binding(self, qq_id: str, username: str) -> UserBinding:
        """添加用户绑定"""
        with self._lock:
            binding = UserBinding(
                qq_id=qq_id,
                username=username,
                bound_at=time.time()
            )
            self._bindings[qq_id] = binding
            self._save_bindings()
            return binding

    def get_binding(self, qq_id: str) -> Optional[UserBinding]:
        """获取用户绑定信息"""
        with self._lock:
            return self._bindings.get(qq_id)

    def remove_binding(self, qq_id: str) -> bool:
        """移除用户绑定"""
        with self._lock:
            if qq_id in self._bindings:
                del self._bindings[qq_id]
                self._save_bindings()
                return True
            return False

    def get_all_bindings(self) -> Dict[str, UserBinding]:
        """获取所有绑定信息"""
        with self._lock:
            return dict(self._bindings)


# 全局数据存储实例
data_store = DataStore()
