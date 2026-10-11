from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    starts_at: datetime
    capacity: int
    available_slots: int


class ReservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    session_id: int
    status: str
    created_at: datetime
    cancelled_at: datetime | None


class ErrorResponse(BaseModel):
    detail: str
