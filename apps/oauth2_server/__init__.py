"""
OAuth2 IDP 路由模块
本服务作为身份提供者的端点
"""
from fastapi import APIRouter

from .authorize import router as authorize_router
from .check_status import router as check_status_router
from .token import router as token_router
from .userinfo import router as userinfo_router

# 主路由
router = APIRouter(prefix="/oauth", tags=["OAuth2 IDP"])

# 注册子路由
router.include_router(authorize_router)
router.include_router(check_status_router)
router.include_router(token_router)
router.include_router(userinfo_router)
