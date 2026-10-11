import pytest
from sqlalchemy import func, select

from conftest import auth
from app.models import EventSession, Reservation


@pytest.mark.behavior("reservation_retry")
def test_retry_does_not_create_a_second_active_reservation(client, db):
    first = client.post("/api/sessions/1/reservations", headers=auth())
    retry = client.post("/api/sessions/1/reservations", headers=auth())

    assert first.status_code == 201
    assert retry.status_code == 409
    active = db.scalar(
        select(func.count()).select_from(Reservation).where(
            Reservation.user_id == 1,
            Reservation.session_id == 1,
            Reservation.status == "active",
        )
    )
    assert active == 1


@pytest.mark.behavior("compatibility")
def test_create_response_shape_and_availability(client, db):
    response = client.post("/api/sessions/1/reservations", headers=auth())
    assert response.status_code == 201
    assert set(response.json()) == {
        "id", "user_id", "session_id", "status", "created_at", "cancelled_at"
    }
    assert response.json()["status"] == "active"
    db.expire_all()
    assert db.get(EventSession, 1).available_slots == 2
