"""预约业务路由"""
import logging
from uuid import uuid4
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.models import ReservationCreate, ReservationResponse, ReservationStatus

logger = logging.getLogger(__name__)
router = APIRouter()

# 内存存储（PoC 演示，生产环境替换为 PostgreSQL）
_store: dict = {}


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建预约",
)
async def create_reservation(payload: ReservationCreate) -> ReservationResponse:
    """
    创建桌位预约。

    - 检查桌位是否可用（PoC 简化为随机成功）
    - 写入数据库并发布预约确认事件
    - 返回预约详情
    """
    reservation_id = uuid4()
    reservation = ReservationResponse(
        id=reservation_id,
        store_id=payload.store_id,
        table_id=payload.table_id,
        member_id=payload.member_id,
        party_size=payload.party_size,
        reserved_at=payload.reserved_at,
        status=ReservationStatus.CONFIRMED,
        created_at=datetime.utcnow(),
        note=payload.note,
    )
    _store[str(reservation_id)] = reservation
    logger.info(
        "reservation created",
        extra={
            "event": "reservation.created",
            "reservation_id": str(reservation_id),
            "store_id": payload.store_id,
            "table_id": payload.table_id,
        },
    )
    return reservation


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="查询预约详情",
)
async def get_reservation(reservation_id: str) -> ReservationResponse:
    """根据预约 ID 查询详情"""
    reservation = _store.get(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found",
        )
    return reservation


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="取消预约",
)
async def cancel_reservation(reservation_id: str) -> None:
    """取消预约（软删除，状态置为 CANCELLED）"""
    reservation = _store.get(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found",
        )
    reservation.status = ReservationStatus.CANCELLED
    logger.info("reservation cancelled", extra={"reservation_id": reservation_id})
