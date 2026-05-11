from __future__ import annotations

import asyncio
from queue import Empty

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...core.runtime.events import event_store
from ...core.services.automation_service import automation_service

router = APIRouter(tags=["events"])


@router.websocket("/ws/events")
async def event_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "status", "data": automation_service.get_status()})
    await websocket.send_json({"type": "logs", "data": automation_service.get_logs(50)})

    subscriber = event_store.subscribe()
    try:
        while True:
            try:
                event = await asyncio.to_thread(subscriber.get, True, 1.0)
            except Empty:
                await websocket.send_json({"type": "status", "data": automation_service.get_status()})
                continue

            await websocket.send_json({"type": "event", "data": event.asdict()})
            await websocket.send_json({"type": "status", "data": automation_service.get_status()})
    except WebSocketDisconnect:
        return
    finally:
        event_store.unsubscribe(subscriber)
