"""
FastAPI 服务端
主入口，注册所有路由
"""
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from apps.base import router as base_router
from apps.oauth2_server import router as oauth2_router

app = FastAPI(title="Onebot-IDP", description="QQ账号绑定服务")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 真实 IP 中间件 - 从 X-Forwarded-For 或 X-Real-IP 头获取真实 IP
@app.middleware("http")
async def get_real_ip_middleware(request: Request, call_next):
    """从代理头中获取真实 IP"""
    # 优先从 X-Forwarded-For 获取
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For 可能包含多个 IP，取第一个
        real_ip = forwarded_for.split(",")[0].strip()
        request.state.real_ip = real_ip
    else:
        # 其次从 X-Real-IP 获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            request.state.real_ip = real_ip
        else:
            # 最后使用直接连接的 IP
            request.state.real_ip = request.client.host if request.client else "unknown"
    
    response = await call_next(request)
    return response


# 注册路由
app.include_router(base_router)
app.include_router(oauth2_router)
