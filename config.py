"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Onebot 配置
ONEBOT_WS_URL = os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:8080")
ONEBOT_ACCESS_TOKEN = os.getenv("ONEBOT_ACCESS_TOKEN", "")
ONEBOT_WS_PING_INTERVAL = int(os.getenv("ONEBOT_WS_PING_INTERVAL", "20"))  # 心跳发送间隔(秒)
ONEBOT_WS_PING_TIMEOUT = int(os.getenv("ONEBOT_WS_PING_TIMEOUT", "20"))  # 心跳超时时间(秒)

# FastAPI 服务配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
BASE_URL = os.getenv("BASE_URL", "https://idp.xxx.com")

# OAuth2 配置
OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID", "your_client_id")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET", "your_client_secret")
OAUTH2_AUTHORIZE_URL = os.getenv("OAUTH2_AUTHORIZE_URL", "https://sso.ineko.cc/application/o/authorize/")
OAUTH2_TOKEN_URL = os.getenv("OAUTH2_TOKEN_URL", "https://sso.ineko.cc/application/o/token/")
OAUTH2_USERINFO_URL = os.getenv("OAUTH2_USERINFO_URL", "https://sso.ineko.cc/application/o/userinfo/")
OAUTH2_REDIRECT_URI = os.getenv("OAUTH2_REDIRECT_URI", f"{BASE_URL}/callback")
OAUTH2_SCOPE = os.getenv("OAUTH2_SCOPE", "openid profile email")
OAUTH2_USERNAME_FIELD = os.getenv("OAUTH2_USERNAME_FIELD", "preferred_username")  # 用户信息中用作用户名的字段

# 数据存储路径
DATA_FILE = os.getenv("DATA_FILE", "bindings.json")

# 绑定链接有效期(秒)
BIND_LINK_EXPIRE_SECONDS = int(os.getenv("BIND_LINK_EXPIRE_SECONDS", "300"))

# 调试模式
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
BIND_LINK_EXPIRE_SECONDS = int(os.getenv("BIND_LINK_EXPIRE_SECONDS", "300"))
