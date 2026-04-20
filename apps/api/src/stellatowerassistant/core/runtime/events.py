from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from queue import Queue
from threading import Lock
from typing import Any
from uuid import uuid4

from ..config.settings import LOG_HISTORY_LIMIT


@dataclass(slots=True)
class RuntimeEvent:
    level: str
    scope: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_type: str = "log"
    id: str = field(default_factory=lambda: uuid4().hex)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def asdict(self) -> dict[str, Any]:
        return asdict(self)


class EventStore:
    def __init__(self, limit: int = LOG_HISTORY_LIMIT) -> None:
        self._events: deque[RuntimeEvent] = deque(maxlen=limit)
        self._subscribers: set[Queue[RuntimeEvent]] = set()
        self._lock = Lock()

    def emit(
        self,
        message: str,
        *,
        level: str = "info",
        scope: str = "automation",
        payload: dict[str, Any] | None = None,
        event_type: str = "log",
    ) -> RuntimeEvent:
        event = RuntimeEvent(
            level=level,
            scope=scope,
            message=message,
            payload=payload or {},
            event_type=event_type,
        )
        with self._lock:
            self._events.appendleft(event)
            subscribers = list(self._subscribers)

        for subscriber in subscribers:
            subscriber.put(event)

        return event

    def recent(self, limit: int = 100) -> list[RuntimeEvent]:
        with self._lock:
            return list(self._events)[:limit]

    def subscribe(self) -> Queue[RuntimeEvent]:
        subscriber: Queue[RuntimeEvent] = Queue()
        with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: Queue[RuntimeEvent]) -> None:
        with self._lock:
            self._subscribers.discard(subscriber)


event_store = EventStore()


def emit_log(
    message: str,
    *,
    level: str = "info",
    scope: str = "automation",
    payload: dict[str, Any] | None = None,
    event_type: str = "log",
) -> RuntimeEvent:
    event = event_store.emit(
        message,
        level=level,
        scope=scope,
        payload=payload,
        event_type=event_type,
    )
    print(message, flush=True)
    return event
