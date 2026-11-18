import time

import pytest
from fastapi.testclient import TestClient

from egg_timer.main import TIMERS, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_timers():
    TIMERS.clear()
    yield
    TIMERS.clear()


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_start_timer():
    r = client.post("/timers", json={"duration_seconds": 300, "label": "soft boiled"})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "running"
    assert body["label"] == "soft boiled"
    assert body["duration_seconds"] == 300


def test_start_rejects_bad_duration():
    assert client.post("/timers", json={"duration_seconds": 0}).status_code == 422
    assert client.post("/timers", json={"duration_seconds": -5}).status_code == 422


def test_get_timer_counts_down():
    tid = client.post("/timers", json={"duration_seconds": 60}).json()["id"]
    time.sleep(0.05)
    body = client.get(f"/timers/{tid}").json()
    assert body["elapsed_seconds"] > 0
    assert body["remaining_seconds"] < 60


def test_timer_finishes():
    tid = client.post("/timers", json={"duration_seconds": 0.05}).json()["id"]
    time.sleep(0.1)
    body = client.get(f"/timers/{tid}").json()
    assert body["status"] == "done"
    assert body["remaining_seconds"] == 0


def test_stop_timer_freezes_time():
    tid = client.post("/timers", json={"duration_seconds": 60}).json()["id"]
    stopped = client.post(f"/timers/{tid}/stop").json()
    assert stopped["status"] == "stopped"
    time.sleep(0.05)
    later = client.get(f"/timers/{tid}").json()
    assert later["elapsed_seconds"] == stopped["elapsed_seconds"]


def test_stop_is_idempotent():
    tid = client.post("/timers", json={"duration_seconds": 60}).json()["id"]
    first = client.post(f"/timers/{tid}/stop").json()
    second = client.post(f"/timers/{tid}/stop").json()
    assert first["elapsed_seconds"] == second["elapsed_seconds"]


def test_list_and_delete():
    tid = client.post("/timers", json={"duration_seconds": 60}).json()["id"]
    assert len(client.get("/timers").json()) == 1
    assert client.delete(f"/timers/{tid}").status_code == 204
    assert client.get("/timers").json() == []


def test_unknown_timer_404():
    assert client.get("/timers/nope").status_code == 404
    assert client.post("/timers/nope/stop").status_code == 404
    assert client.delete("/timers/nope").status_code == 404
