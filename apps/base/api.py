"""
/api 端点
绑定信息查询接口
"""
from fastapi import APIRouter, HTTPException, Request

from core.storage import data_store

router = APIRouter()


@router.get("/status")
async def get_status(request: Request):
    """获取服务状态"""
    real_ip = getattr(request.state, 'real_ip', request.client.host if request.client else "unknown")
    return {"service": "Onebot-IDP", "status": "running", "your_ip": real_ip}


@router.get("/bindings")
async def get_bindings():
    """获取所有绑定信息 (仅供调试)"""
    bindings = data_store.get_all_bindings()
    return {
        uin: {
            "username": b.username,
            "bound_at": b.bound_at
        }
        for uin, b in bindings.items()
    }


@router.get("/binding/{uin}")
async def get_binding(uin: str):
    """查询特定 QQ 的绑定信息"""
    binding = data_store.get_binding(uin)
    if not binding:
        raise HTTPException(status_code=404, detail="未找到绑定信息")
    
    return {
        "uin": binding.uin,
        "username": binding.username,
        "bound_at": binding.bound_at
    }
