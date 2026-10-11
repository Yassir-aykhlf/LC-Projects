import pytest

from conftest import auth


@pytest.mark.behavior("state_isolation")
def test_dashboard_is_scoped_to_authenticated_user(client):
    own = client.post("/api/sessions/1/reservations", headers=auth(1)).json()
    other = client.post("/api/sessions/1/reservations", headers=auth(2)).json()

    rows = client.get("/api/reservations/me?status=active", headers=auth(1)).json()
    assert [row["id"] for row in rows] == [own["id"]]
    assert other["id"] not in [row["id"] for row in rows]
