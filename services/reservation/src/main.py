"""预约服务 FastAPI 应用入口"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers import reservations, health
from src.telemetry import setup_telemetry

# 结构化日志配置
logging.basicConfig(
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"reservation-svc","message":"%(message)s"}',
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("reservation-svc starting up", extra={"event": "startup"})
    setup_telemetry()
    yield
    logger.info("reservation-svc shutting down", extra={"event": "shutdown"})


app = FastAPI(
    title="NekoCafé 预约服务",
    description="桌位选座、预付定金、满位排队核心服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境须限制
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router)
app.include_router(reservations.router, prefix="/api/v1/reservations", tags=["reservations"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8080, reload=False)
