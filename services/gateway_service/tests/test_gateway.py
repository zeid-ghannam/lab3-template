from http import HTTPStatus


def test_health_check(client):
    response = client.get("/manage/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"status": "OK"}


def test_get_hotels(client):
    response = client.get("/api/v1/hotels")
    assert response.status_code == HTTPStatus.OK
    assert "items" in response.json
