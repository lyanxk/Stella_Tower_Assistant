from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..config.settings import PAUSE_POLL_INTERVAL
from .events import emit_log


@dataclass(slots=True)
class RuntimeState:
    paused: bool = False
    skip_initial_wait: bool = False
    running: bool = True
    current_run: int = 0
    max_runs: int = 0
    last_error: str | None = None
    last_message: str = "Idle"
    started_at: str | None = None
    finished_at: str | None = None
    elevator_floor: int | None = None
    current_gold: int | None = None

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        self.last_message = "Paused" if self.paused else "Running"
        emit_log("[Hotkey] Paused" if self.paused else "[Hotkey] Resumed", scope="runtime")

    def mark_skip_initial(self) -> None:
        self.skip_initial_wait = True
        self.last_message = "Skip initial waits enabled"
        emit_log("[Hotkey] Skip initial waits enabled", scope="runtime")

    def stop(self) -> None:
        self.running = False
        self.finished_at = datetime.now(timezone.utc).isoformat()
        self.last_message = "Stop requested"
        emit_log("[Hotkey] Stop requested", scope="runtime")

    def reset_initial_wait(self) -> None:
        self.skip_initial_wait = False

    def reset_for_start(self, max_runs: int) -> None:
        self.paused = False
        self.skip_initial_wait = False
        self.running = True
        self.current_run = 0
        self.max_runs = max_runs
        self.last_error = None
        self.last_message = "Starting automation"
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.finished_at = None
        self.elevator_floor = None
        self.current_gold = None

    def mark_run(self, current_run: int, max_runs: int) -> None:
        self.current_run = current_run
        self.max_runs = max_runs
        self.last_message = f"Run {current_run}/{max_runs} in progress"

    def mark_error(self, message: str) -> None:
        self.last_error = message
        self.last_message = "Error"

    def mark_ocr_reading(self, *, elevator_floor: int | None, current_gold: int | None) -> None:
        if elevator_floor is not None:
            self.elevator_floor = elevator_floor
        if current_gold is not None:
            self.current_gold = current_gold

    def mark_finished(self, message: str = "Automation finished") -> None:
        self.running = False
        self.paused = False
        self.last_message = message
        self.finished_at = datetime.now(timezone.utc).isoformat()

    def snapshot(self, *, thread_alive: bool) -> dict[str, Any]:
        return {
            "is_running": self.running and thread_alive,
            "is_paused": self.paused,
            "skip_initial_wait": self.skip_initial_wait,
            "current_run": self.current_run,
            "max_runs": self.max_runs,
            "last_error": self.last_error,
            "last_message": self.last_message,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "elevator_floor": self.elevator_floor,
            "current_gold": self.current_gold,
            "thread_alive": thread_alive,
        }

    def check_pause_and_running(self) -> None:
        if not self.running:
            raise KeyboardInterrupt("User requested stop")

        while self.paused and self.running:
            time.sleep(PAUSE_POLL_INTERVAL)

        if not self.running:
            raise KeyboardInterrupt("User requested stop")


state = RuntimeState()
