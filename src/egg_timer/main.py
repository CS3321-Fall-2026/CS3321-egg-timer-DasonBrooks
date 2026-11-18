"""A simple egg timer API: start, check, and stop timers."""

import time
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Egg Timer API", version="0.1.0")


class StartRequest(BaseModel):
    duration_seconds: float = Field(gt=0, le=86400, description="How long the timer runs")
    label: str = Field(default="egg", max_length=100)


class Timer:
    def __init__(self, duration: float, label: str) -> None:
        self.id = uuid.uuid4().hex[:8]
        self.label = label
        self.duration = duration
        self.started_at = time.monotonic()
        self.stopped_at: float | None = None

    def elapsed(self) -> float:
        end = self.stopped_at if self.stopped_at is not None else time.monotonic()
        return end - self.started_at

    def remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed())

    def status(self) -> str:
        if self.stopped_at is not None:
            return "stopped"
        return "done" if self.remaining() == 0 else "running"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "duration_seconds": self.duration,
            "elapsed_seconds": round(self.elapsed(), 3),
            "remaining_seconds": round(self.remaining(), 3),
            "status": self.status(),
        }


TIMERS: dict[str, Timer] = {}


def _get(timer_id: str) -> Timer:
    timer = TIMERS.get(timer_id)
    if timer is None:
        raise HTTPException(status_code=404, detail="Timer not found")
    return timer


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/timers", status_code=201)
def start_timer(body: StartRequest) -> dict:
    timer = Timer(body.duration_seconds, body.label)
    TIMERS[timer.id] = timer
    return timer.to_dict()


@app.get("/timers")
def list_timers() -> list[dict]:
    return [t.to_dict() for t in TIMERS.values()]


@app.get("/timers/{timer_id}")
def get_timer(timer_id: str) -> dict:
    return _get(timer_id).to_dict()


@app.post("/timers/{timer_id}/stop")
def stop_timer(timer_id: str) -> dict:
    timer = _get(timer_id)
    if timer.stopped_at is None:
        timer.stopped_at = time.monotonic()
    return timer.to_dict()


@app.delete("/timers/{timer_id}", status_code=204)
def delete_timer(timer_id: str) -> None:
    _get(timer_id)
    del TIMERS[timer_id]
