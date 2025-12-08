"""
主程序入口
同时运行 FastAPI 服务器和 Onebot 机器人
"""
import asyncio
import os
import sys
import uvicorn
from contextlib import asynccontextmanager


# 默认配置模板
DEFAULT_CONFIG = """# Onebot-IDP 配置文件
# 请根据实际情况修改以下配置

# ==================== Onebot 配置 ====================
# Onebot WebSocket 地址
ONEBOT_WS_URL=ws://127.0.0.1:8080
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

# ==================== OAuth2 配置 ====================
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
OAUTH2_SCOPE=openid profile
# 用户信息中用作用户名的字段（常见值：preferred_username, username, name, sub）
OAUTH2_USERNAME_FIELD=preferred_username

# ==================== 其他配置 ====================
# 绑定数据存储文件
DATA_FILE=bindings.json
# 绑定链接有效期（秒）
BIND_LINK_EXPIRE_SECONDS=300
# 调试模式（输出详细的OAuth2请求响应信息）
DEBUG=false
"""


def check_and_generate_config():
    """检查并生成配置文件"""
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    
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


# 首先检查配置文件
check_and_generate_config()

# 配置文件存在后再导入其他模块
from server import app
from bot import bot_client, bot_handler
import config


async def run_bot():
    """运行机器人"""
    print("启动 Onebot 机器人...")
    await bot_client.run()


async def run_server():
    """运行 FastAPI 服务器"""
    print(f"启动 FastAPI 服务器: {config.SERVER_HOST}:{config.SERVER_PORT}")
    server_config = uvicorn.Config(
        app,
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        log_level="info"
    )
    server = uvicorn.Server(server_config)
    await server.serve()


async def main():
    """主函数"""
    print("=" * 50)
    print("Onebot-IDP 服务启动中...")
    print("=" * 50)
    print(f"服务地址: {config.BASE_URL}")
    print(f"Onebot WS: {config.ONEBOT_WS_URL}")
    print(f"OAuth2 授权: {config.OAUTH2_AUTHORIZE_URL}")
    print("=" * 50)
    
    # 同时运行服务器和机器人
    await asyncio.gather(
        run_server(),
        run_bot()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n服务已停止")
