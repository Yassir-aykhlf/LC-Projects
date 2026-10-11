from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EventSession, Reservation, ReservationAudit


class ReservationConflict(Exception):
    pass


class ReservationNotFound(Exception):
    pass


def reserve(db: Session, *, session_id: int, user_id: int) -> Reservation:
    event_session = db.get(EventSession, session_id)
    if event_session.available_slots <= 0:
        raise ReservationConflict("Session is full")

    now = datetime.now(UTC)
    reservation = Reservation(
        user_id=user_id,
        session_id=event_session.id,
        status="active",
        created_at=now,
    )
    event_session.available_slots -= 1
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    db.add(
        ReservationAudit(
            reservation_id=reservation.id,
            action="created",
            actor_user_id=user_id,
            created_at=now,
        )
    )
    db.commit()
    return reservation


def cancel(db: Session, *, reservation_id: int, user_id: int) -> Reservation:
    reservation = db.scalar(select(Reservation).where(Reservation.id == reservation_id))
    if reservation is None:
        raise ReservationNotFound("Reservation not found")

    reservation.status = "cancelled"
    reservation.cancelled_at = datetime.now(UTC)
    event_session = db.get(EventSession, reservation.session_id)
    event_session.available_slots += 1
    db.commit()

    db.add(
        ReservationAudit(
            reservation_id=reservation.id,
            action="cancelled",
            actor_user_id=user_id,
            created_at=datetime.now(UTC),
        )
    )
    db.commit()
    db.refresh(reservation)
    return reservation
