"""
FastAPI 服务端
提供 OAuth2 回调和绑定页面
"""
import asyncio
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

import config
from storage import data_store
from oauth2_client import oauth2_client
from bot import bot_client

app = FastAPI(title="Onebot-IDP", description="QQ账号绑定服务")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 成功页面 HTML
SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>绑定成功</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
        }}
        .success-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #27ae60;
            margin-bottom: 16px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
        .username {{
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>绑定成功!</h1>
        <p>您已成功将 QQ 账号绑定到用户 <span class="username">{username}</span></p>
        <p>您可以关闭此页面了。</p>
    </div>
</body>
</html>
"""

# 失败页面 HTML
ERROR_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>绑定失败</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
        }}
        .error-icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #e74c3c;
            margin-bottom: 16px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
        .error-msg {{
            background: #fee;
            padding: 12px;
            border-radius: 8px;
            color: #c0392b;
            margin-top: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">❌</div>
        <h1>绑定失败</h1>
        <p class="error-msg">{error}</p>
        <p>请返回 QQ 重新发起绑定请求。</p>
    </div>
</body>
</html>
"""


async def notify_user(user_id: int, message: str):
    """后台发送通知给用户"""
    try:
        await bot_client.send_private_msg(user_id, message)
    except Exception as e:
        print(f"发送通知失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {"service": "Onebot-IDP", "status": "running"}


@app.get("/bind/{bind_code}")
async def bind_page(bind_code: str):
    """
    绑定页面 - 用户点击绑定链接后的入口
    重定向到 OAuth2 授权页面
    """
    # 检查会话是否存在且有效
    session = data_store.get_session_by_code(bind_code)
    if not session:
        return HTMLResponse(
            ERROR_HTML.format(error="绑定链接无效或已过期，请重新发起绑定请求"),
            status_code=400
        )
    
    # 生成 OAuth2 授权 URL 并重定向
    auth_url = oauth2_client.get_authorization_url(session.state)
    return RedirectResponse(url=auth_url)


@app.get("/callback")
async def oauth_callback(code: str = None, state: str = None, error: str = None):
    """
    OAuth2 回调处理
    SSO 服务器授权后会重定向到这里
    """
    # 处理授权错误
    if error:
        return HTMLResponse(
            ERROR_HTML.format(error=f"授权失败: {error}"),
            status_code=400
        )
    
    # 验证参数
    if not code or not state:
        return HTMLResponse(
            ERROR_HTML.format(error="缺少必要参数"),
            status_code=400
        )
    
    # 通过 state 获取会话
    session = data_store.get_session_by_state(state)
    if not session:
        return HTMLResponse(
            ERROR_HTML.format(error="会话无效或已过期，请重新发起绑定请求"),
            status_code=400
        )
    
    # 使用授权码获取用户名
    actual_username, error_msg = await oauth2_client.get_username_from_code(code)
    if not actual_username:
        display_error = f"获取用户信息失败: {error_msg}" if error_msg else "获取用户信息失败，请重试"
        return HTMLResponse(
            ERROR_HTML.format(error=display_error),
            status_code=500
        )
    
    # 验证用户名是否匹配
    if session.expected_username and actual_username.lower() != session.expected_username.lower():
        error_msg = (
            f"用户名不匹配！\n"
            f"期望: {session.expected_username}\n"
            f"实际: {actual_username}\n"
            f"请确认您使用正确的账号登录"
        )
        
        # 清理会话
        data_store.remove_session(session.bind_code)
        
        # 后台发送通知
        asyncio.create_task(notify_user(
            int(session.qq_id),
            f"绑定失败: 用户名不匹配\n期望绑定: {session.expected_username}\n实际登录: {actual_username}"
        ))
        
        return HTMLResponse(
            ERROR_HTML.format(error=error_msg.replace('\n', '<br>')),
            status_code=400
        )
    
    # 绑定成功
    data_store.add_binding(session.qq_id, actual_username)
    
    # 清理会话
    data_store.remove_session(session.bind_code)
    
    # 后台发送通知
    asyncio.create_task(notify_user(
        int(session.qq_id),
        f"🎉 绑定成功！\n您的 QQ 已成功绑定到账号: {actual_username}"
    ))
    
    return HTMLResponse(SUCCESS_HTML.format(username=actual_username))


@app.get("/api/bindings")
async def get_bindings():
    """获取所有绑定信息 (仅供调试)"""
    bindings = data_store.get_all_bindings()
    return {
        qq_id: {
            "username": b.username,
            "bound_at": b.bound_at
        }
        for qq_id, b in bindings.items()
    }


@app.get("/api/binding/{qq_id}")
async def get_binding(qq_id: str):
    """查询特定 QQ 的绑定信息"""
    binding = data_store.get_binding(qq_id)
    if not binding:
        raise HTTPException(status_code=404, detail="未找到绑定信息")
    
    return {
        "qq_id": binding.qq_id,
        "username": binding.username,
        "bound_at": binding.bound_at
    }
