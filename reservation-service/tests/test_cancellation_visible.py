import pytest

from conftest import auth


@pytest.mark.behavior("reserve_after_cancel")
def test_user_can_reserve_again_after_cancelling(client):
    first = client.post("/api/sessions/1/reservations", headers=auth())
    cancelled = client.post(f"/api/reservations/{first.json()['id']}/cancel", headers=auth())
    second = client.post("/api/sessions/1/reservations", headers=auth())

    assert first.status_code == 201
    assert cancelled.status_code == 200
    assert second.status_code == 201
    assert second.json()["id"] != first.json()["id"]
