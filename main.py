"""
主程序入口
同时运行 FastAPI 服务器和 Onebot 机器人
"""
import asyncio
import uvicorn
from contextlib import asynccontextmanager

from text.config_example_generator import check_and_generate_config


# 首先检查配置文件
check_and_generate_config()

# 配置文件存在后再导入其他模块
from core.server import app
from core.onebot import bot_client
from core.bot import bot_handler
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
    print(f"Onebot 模式: {config.ONEBOT_MODE}")
    if config.ONEBOT_MODE.lower() == 'server':
        print(f"Onebot WS 服务端: {config.ONEBOT_WS_HOST}:{config.ONEBOT_WS_PORT}")
    else:
        print(f"Onebot WS 客户端: {config.ONEBOT_WS_URL}")
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
