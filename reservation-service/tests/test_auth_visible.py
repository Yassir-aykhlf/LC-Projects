import pytest


@pytest.mark.behavior("compatibility")
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("post", "/api/sessions/1/reservations"),
        ("get", "/api/reservations/me?status=active"),
        ("post", "/api/reservations/1/cancel"),
    ],
)
def test_protected_endpoints_require_authentication(client, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401


@pytest.mark.behavior("compatibility")
def test_session_listing_remains_public(client):
    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert [row["id"] for row in response.json()] == [1, 2, 3]
