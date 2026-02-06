# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_status_and_uptime():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "OK"
    assert isinstance(body["uptime_seconds"], int)
    assert body["uptime_seconds"] >= 0