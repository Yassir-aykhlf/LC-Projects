from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))


class EventSession(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint("capacity >= 0", name="ck_sessions_capacity_nonnegative"),
        CheckConstraint("available_slots >= 0", name="ck_sessions_slots_nonnegative"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    capacity: Mapped[int] = mapped_column(Integer)
    available_slots: Mapped[int] = mapped_column(Integer)
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="event_session")


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = (CheckConstraint("status IN ('active', 'cancelled')", name="ck_reservation_status"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    event_session: Mapped[EventSession] = relationship(back_populates="reservations")
    audits: Mapped[list["ReservationAudit"]] = relationship(back_populates="reservation")


class ReservationAudit(Base):
    __tablename__ = "reservation_audits"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    action: Mapped[str] = mapped_column(String(32))
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reservation: Mapped[Reservation] = relationship(back_populates="audits")
