"""健康检查路由"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/healthz", tags=["health"], summary="健康检查")
async def health_check():
    """Kubernetes liveness / readiness probe 端点"""
    return JSONResponse(
        content={"status": "ok", "service": "reservation-svc"},
        status_code=200,
    )


@router.get("/readyz", tags=["health"], summary="就绪检查")
async def readiness_check():
    """就绪探针：检查数据库连接"""
    # TODO: 实际环境中检查 DB 连接
    return JSONResponse(
        content={"status": "ready"},
        status_code=200,
    )
