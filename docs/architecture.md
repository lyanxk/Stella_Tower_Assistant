# Stella Tower Assistant Architecture

## Overview

This repository now uses a two-application layout:

- `apps/api`: Python automation engine, local HTTP API, WebSocket event stream.
- `apps/web`: Vue 3 + Vite control console for local operation.

The browser does not execute automation directly. It talks to the Python backend over localhost:

- HTTP for commands and snapshots.
- WebSocket for runtime events and status updates.

## Backend layout

- `src/stellatowerassistant/cli.py`: command entrypoint.
- `src/stellatowerassistant/api/`: FastAPI app, routes, schemas, websocket endpoint.
- `src/stellatowerassistant/core/automation/`: existing image matching and click logic.
- `src/stellatowerassistant/core/runtime/`: runtime state and event buffer.
- `src/stellatowerassistant/core/services/`: service layer exposed to API routes.
- `assets/templates/`: template image assets.
- `tests/`: lightweight unit tests for stable backend pieces.

## Frontend layout

- `src/app/router/`: route declarations.
- `src/app/layouts/`: shell layout.
- `src/pages/`: route-level pages.
- `src/features/`: domain-specific panels.
- `src/widgets/`: reusable dashboard blocks.
- `src/shared/`: API client, types, styles.

## Runtime flow

1. User opens the Vue console.
2. Vue requests current status, logs, settings, and emulator info from FastAPI.
3. User starts automation with `POST /api/automation/start`.
4. Backend launches the automation worker in a background thread.
5. Worker emits events into the runtime event store.
6. Vue listens on `/ws/events` and updates dashboard state in real time.

## Next recommended improvements

- Move hardcoded thresholds into editable config persistence.
- Add structured event types for run progress, shop entry, and recognition failures.
- Add image/template inspection tooling in the templates page.
- Add packaging for a single-command local launch script.
