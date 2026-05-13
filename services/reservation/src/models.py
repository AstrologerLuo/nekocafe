"""预约服务数据模型"""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ReservationStatus(str, Enum):
    PENDING = "pending"       # 待确认
    CONFIRMED = "confirmed"   # 已确认
    CHECKED_IN = "checked_in" # 已入座
    CANCELLED = "cancelled"   # 已取消
    NO_SHOW = "no_show"       # 未到店


class ReservationCreate(BaseModel):
    """创建预约请求体"""
    store_id: int = Field(..., description="门店 ID", gt=0)
    table_id: int = Field(..., description="桌位 ID", gt=0)
    member_id: int = Field(..., description="会员 ID", gt=0)
    party_size: int = Field(..., description="就餐人数", ge=1, le=20)
    reserved_at: datetime = Field(..., description="预约时间（UTC）")
    note: str | None = Field(None, description="备注", max_length=200)


class ReservationResponse(BaseModel):
    """预约响应体"""
    id: UUID = Field(default_factory=uuid4)
    store_id: int
    table_id: int
    member_id: int
    party_size: int
    reserved_at: datetime
    status: ReservationStatus = ReservationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    note: str | None = None

    model_config = {"from_attributes": True}
