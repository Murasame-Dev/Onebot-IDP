"""
默认配置模板
首次运行时自动生成 .env 文件
"""
import os
import sys

DEFAULT_CONFIG = """# Onebot-IDP 配置文件
# 请根据实际情况修改以下配置

# ==================== Onebot 配置 ====================
# 连接模式: client(主动连接到Onebot) 或 server(等待Onebot连接)
ONEBOT_MODE=client
# client模式: Onebot服务器WebSocket地址
ONEBOT_WS_URL=ws://127.0.0.1:8080
# server模式: WebSocket服务端监听地址
ONEBOT_WS_HOST=0.0.0.0
# server模式: WebSocket服务端监听端口
ONEBOT_WS_PORT=8080
# Onebot 访问令牌（如果有）
ONEBOT_ACCESS_TOKEN=
# WebSocket 心跳发送间隔（秒）
ONEBOT_WS_PING_INTERVAL=20
# WebSocket 心跳超时时间（秒）
ONEBOT_WS_PING_TIMEOUT=20

# ==================== FastAPI 服务配置 ====================
# 服务监听地址
SERVER_HOST=0.0.0.0
# 服务监听端口
SERVER_PORT=8000
# 服务公网地址（用于生成绑定链接）
BASE_URL=https://idp.xxx.com

# ==================== OAuth2 配置（本服务作为客户端） ====================
# OAuth2 客户端 ID
OAUTH2_CLIENT_ID=your_client_id
# OAuth2 客户端密钥
OAUTH2_CLIENT_SECRET=your_client_secret
# OAuth2 授权端点
OAUTH2_AUTHORIZE_URL=https://sso.xxx.com/oauth2/authorize
# OAuth2 Token 端点
OAUTH2_TOKEN_URL=https://sso.xxx.com/oauth2/token
# OAuth2 用户信息端点
OAUTH2_USERINFO_URL=https://sso.xxx.com/oauth2/userinfo
# OAuth2 回调地址（需与 SSO 服务器配置一致）
OAUTH2_REDIRECT_URI=https://idp.xxx.com/callback
# OAuth2 Scope
OAUTH2_SCOPE=openid profile email
# 用户信息中用作用户名的字段（常见值：preferred_username, username, name, sub）
OAUTH2_USERNAME_FIELD=preferred_username

# ==================== 数据存储配置 ====================
# 绑定数据存储文件
DATA_FILE=./data/bindings.json
# 绑定链接有效期（秒）
BIND_LINK_EXPIRE_SECONDS=300
# 绑定时额外记录的用户信息字段（逗号分隔，可选: email,email_verified,name,preferred_username,nickname,sub,groups 等）
BIND_RECORD_FIELDS=

# ==================== 命令配置 ====================
# 命令前缀
CMD_PREFIX=/
# 绑定命令名称
CMD_BIND=bind
# 取消绑定请求命令名称
CMD_BIND_CANCEL=bind_cancel
# 解绑命令名称
CMD_UNBIND=unbind
# 状态查询命令名称
CMD_STATUS=status
# 登录授权命令名称
CMD_LOGIN=login

# ==================== OAuth2 IDP 配置（本服务作为身份提供者） ====================
# 是否启用 IDP 功能
IDP_ENABLED=true
# 第三方应用的 client_id
IDP_CLIENT_ID=your_app_client_id
# 第三方应用的 client_secret
IDP_CLIENT_SECRET=your_app_client_secret
# 允许的回调地址列表（逗号分隔）
IDP_ALLOWED_REDIRECT_URIS=
# /oauth/userinfo 端点输出的字段（逗号分隔，可选: sub,preferred_username,username,uin,email,name,nickname 等）
IDP_USERINFO_OUTPUT_FIELDS=sub,preferred_username,username,uin
# 登录验证码有效期（秒）
LOGIN_CODE_EXPIRE_SECONDS=180

# ==================== 调试配置 ====================
# 调试模式（输出详细的OAuth2请求响应信息）
DEBUG=false
"""

def check_and_generate_config():
    """检查并生成配置文件"""
    # 获取上一级目录（项目根目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    env_file = os.path.join(parent_dir, ".env")
    
    if not os.path.exists(env_file):
        print("=" * 50)
        print("⚠️  未检测到配置文件，正在生成默认配置...")
        print("=" * 50)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(DEFAULT_CONFIG)
        
        print(f"✅ 配置文件已生成: {env_file}")
        print()
        print("请编辑配置文件后重新运行程序")
        print("需要配置的关键项:")
        print("  - ONEBOT_WS_URL: Onebot WebSocket 地址")
        print("  - BASE_URL: 服务公网地址")
        print("  - OAUTH2_CLIENT_ID: OAuth2 客户端 ID")
        print("  - OAUTH2_CLIENT_SECRET: OAuth2 客户端密钥")
        print("  - OAUTH2_* URLs: OAuth2 各端点地址")
        print("=" * 50)
        sys.exit(0)
    
    return True