# tests/test_process.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_process_valid():
    r = client.post("/process", json={"value": 3})
    assert r.status_code == 200
    body = r.json()
    # process_value doubles the input
    assert body["input"] == 3
    assert body["result"] == 6


def test_process_negative_and_zero():
    # zero
    r = client.post("/process", json={"value": 0})
    assert r.status_code == 200
    assert r.json()["result"] == 0
    # negative
    r = client.post("/process", json={"value": -2.5})
    assert r.status_code == 200
    assert r.json()["result"] == -5.0


def test_process_invalid_type():
    r = client.post("/process", json={"value": "not-a-number"})
    # Pydantic will reject non-numeric
    assert r.status_code == 422