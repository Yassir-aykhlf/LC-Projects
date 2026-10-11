from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import CurrentUser
from ..db import get_db
from ..models import Reservation
from ..schemas import ReservationResponse
from ..services.reservation_service import (
    ReservationConflict,
    ReservationNotFound,
    cancel,
    reserve,
)

router = APIRouter(tags=["reservations"])


@router.post(
    "/api/sessions/{session_id}/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reservation(session_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    try:
        return reserve(db, session_id=session_id, user_id=user.id)
    except ReservationConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get("/api/reservations/me", response_model=list[ReservationResponse])
def my_reservations(
    user: CurrentUser,
    status_filter: Literal["active", "cancelled"] = Query(alias="status"),
    db: Session = Depends(get_db),
):
    query = select(Reservation).where(Reservation.user_id == user.id)
    if status_filter == "cancelled":
        query = query.where(Reservation.status == "cancelled")
    return db.scalars(query.order_by(Reservation.created_at.desc())).all()


@router.post(
    "/api/reservations/{reservation_id}/cancel",
    response_model=ReservationResponse,
)
def cancel_reservation(reservation_id: int, user: CurrentUser, db: Session = Depends(get_db)):
    try:
        return cancel(db, reservation_id=reservation_id, user_id=user.id)
    except ReservationNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
