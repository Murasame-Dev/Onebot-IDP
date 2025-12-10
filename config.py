"""
配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Onebot 配置
ONEBOT_MODE = os.getenv("ONEBOT_MODE", "client")  # client: 连接到Onebot, server: 等待Onebot连接
ONEBOT_WS_URL = os.getenv("ONEBOT_WS_URL", "ws://127.0.0.1:8080")  # client模式: Onebot服务器地址
ONEBOT_WS_HOST = os.getenv("ONEBOT_WS_HOST", "0.0.0.0")  # server模式: 监听地址
ONEBOT_WS_PORT = int(os.getenv("ONEBOT_WS_PORT", "8080"))  # server模式: 监听端口
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

# 绑定时额外记录的用户信息字段（逗号分隔，可选: email,email_verified,name,preferred_username,nickname,sub,groups 等）
BIND_RECORD_FIELDS = [f.strip() for f in os.getenv("BIND_RECORD_FIELDS", "").split(",") if f.strip()]

# 登录验证码有效期(秒)
LOGIN_CODE_EXPIRE_SECONDS = int(os.getenv("LOGIN_CODE_EXPIRE_SECONDS", "180"))

# OAuth2 IDP 配置 (本服务作为身份提供者)
IDP_ENABLED = os.getenv("IDP_ENABLED", "true").lower() in ("true", "1", "yes")
IDP_CLIENT_ID = os.getenv("IDP_CLIENT_ID", "your_app_client_id")  # 第三方应用的 client_id
IDP_CLIENT_SECRET = os.getenv("IDP_CLIENT_SECRET", "your_app_client_secret")  # 第三方应用的 client_secret
IDP_ALLOWED_REDIRECT_URIS = os.getenv("IDP_ALLOWED_REDIRECT_URIS", "").split(",")  # 允许的回调地址列表
IDP_USERINFO_OUTPUT_FIELDS = [f.strip() for f in os.getenv("IDP_USERINFO_OUTPUT_FIELDS", "sub,preferred_username,username,uin").split(",") if f.strip()]  # userinfo 端点输出字段

# 调试模式
DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# 命令配置
CMD_PREFIX = os.getenv("CMD_PREFIX", "/")  # 命令前缀
CMD_BIND = os.getenv("CMD_BIND", "bind")  # 绑定命令
CMD_BIND_CANCEL = os.getenv("CMD_BIND_CANCEL", "bind_cancel")  # 取消绑定请求命令
CMD_UNBIND = os.getenv("CMD_UNBIND", "unbind")  # 解绑命令
CMD_STATUS = os.getenv("CMD_STATUS", "status")  # 状态查询命令
CMD_LOGIN = os.getenv("CMD_LOGIN", "login")  # 登录授权命令

# 完整命令（前缀 + 命令名）
FULL_CMD_BIND = f"{CMD_PREFIX}{CMD_BIND}"
FULL_CMD_BIND_CANCEL = f"{CMD_PREFIX}{CMD_BIND_CANCEL}"
FULL_CMD_UNBIND = f"{CMD_PREFIX}{CMD_UNBIND}"
FULL_CMD_STATUS = f"{CMD_PREFIX}{CMD_STATUS}"
FULL_CMD_LOGIN = f"{CMD_PREFIX}{CMD_LOGIN}"
