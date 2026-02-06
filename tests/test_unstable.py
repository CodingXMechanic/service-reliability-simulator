# tests/test_unstable.py
from fastapi.testclient import TestClient
import app.utils as utils_module
from app.main import app
import random

client = TestClient(app)


def test_unstable_success(monkeypatch):
    # Force random.choice -> "success"
    monkeypatch.setattr(utils_module.random, "choice", lambda seq: "success")
    r = client.get("/unstable")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_unstable_exception(monkeypatch):
    # Force exception path
    monkeypatch.setattr(utils_module.random, "choice", lambda seq: "exception")
    r = client.get("/unstable")
    # After retries, endpoint should return HTTP 500
    assert r.status_code == 500


def test_unstable_delay_timeout(monkeypatch):
    # Force delay path which will trigger timeout (asyncio.wait_for in code)
    monkeypatch.setattr(utils_module.random, "choice", lambda seq: "delay")
    r = client.get("/unstable")
    # Should result in a 504 Gateway Timeout response
    assert r.status_code == 504