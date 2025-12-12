"""
基础路由模块
"""
from fastapi import APIRouter, Request

from .bind import router as bind_router
from .callback import router as callback_router
# from .api import router as api_router

# 主路由
router = APIRouter()


def get_real_ip(request: Request) -> str:
    """获取请求的真实 IP"""
    return getattr(request.state, 'real_ip', request.client.host if request.client else "unknown")


@router.get("/")
async def root(request: Request):
    """根路径 - 服务状态"""
    real_ip = get_real_ip(request)
    return {"service": "Onebot-IDP", "status": "running", "your_ip": real_ip}


# 注册子路由
router.include_router(bind_router)
router.include_router(callback_router)
# router.include_router(api_router, prefix="/api", tags=["API"])
