# API Contract

Base URL: `http://127.0.0.1:8765`

## Health

- `GET /health`
  - Returns backend status and current emulator window snapshot.

## Automation

- `GET /api/automation/status`
  - Returns runtime state.
- `GET /api/automation/logs?limit=100`
  - Returns recent log events.
- `POST /api/automation/start`
  - Starts the automation worker if not already running.
- `POST /api/automation/pause`
  - Toggles runtime into paused state.
- `POST /api/automation/resume`
  - Resumes a paused worker.
- `POST /api/automation/stop`
  - Requests the worker to stop.

## Settings

- `GET /api/settings`
  - Returns readonly config snapshot used by the backend.

## Templates

- `GET /api/templates`
  - Lists configured template keys and whether the asset file exists.

## Emulator

- `GET /api/emulator/window`
  - Returns emulator detection info.
- `GET /api/emulator/screenshot`
  - Returns a base64 PNG screenshot.

## WebSocket

- `GET /ws/events`
  - Sends three message forms:
  - `{"type":"status","data": ... }`
  - `{"type":"logs","data": [...] }`
  - `{"type":"event","data": {...} }`

## Core response shapes

### Automation status

```json
{
  "is_running": false,
  "is_paused": false,
  "current_run": 0,
  "max_runs": 7,
  "last_error": null,
  "last_message": "Idle",
  "started_at": null,
  "finished_at": null,
  "thread_alive": false
}
```

### Action response

```json
{
  "ok": true,
  "message": "Automation started."
}
```
