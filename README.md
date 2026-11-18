# Egg Timer API

A tiny FastAPI service for starting, checking, and stopping egg timers.

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/health` | Liveness check |
| POST | `/timers` | Start a timer: `{"duration_seconds": 300, "label": "soft boiled"}` |
| GET | `/timers` | List all timers |
| GET | `/timers/{id}` | Check elapsed and remaining time |
| POST | `/timers/{id}/stop` | Stop a timer (freezes elapsed time) |
| DELETE | `/timers/{id}` | Remove a timer |

Interactive docs are at `/docs` when the server is running.

## Run with Docker

```bash
docker build -t egg-timer .
docker run --rm -p 8000:8000 --name egg-timer egg-timer
```

The image build installs dependencies with `uv sync --all-extras --all-groups`, runs `pytest`
(the build fails if tests fail), builds a wheel, and starts the app.

## Try it

```bash
curl -X POST localhost:8000/timers -H "Content-Type: application/json" \
  -d '{"duration_seconds": 300, "label": "soft boiled"}'
curl localhost:8000/timers/<id>
curl -X POST localhost:8000/timers/<id>/stop
```

## Run locally without Docker

```bash
uv sync --all-extras --all-groups
uv run pytest
uv run uvicorn egg_timer.main:app --reload
```
