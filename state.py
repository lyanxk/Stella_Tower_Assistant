from __future__ import annotations

import time
from dataclasses import dataclass

from config import PAUSE_POLL_INTERVAL


@dataclass(slots=True)
class RuntimeState:
    paused: bool = False
    skip_initial_wait: bool = False
    running: bool = True

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        print("[Hotkey] Paused" if self.paused else "[Hotkey] Resumed")

    def mark_skip_initial(self) -> None:
        self.skip_initial_wait = True
        print("[Hotkey] Skip initial waits enabled")

    def stop(self) -> None:
        self.running = False
        print("[Hotkey] Stop requested")

    def reset_initial_wait(self) -> None:
        self.skip_initial_wait = False

    def check_pause_and_running(self) -> None:
        if not self.running:
            raise KeyboardInterrupt("User requested stop")

        while self.paused and self.running:
            time.sleep(PAUSE_POLL_INTERVAL)

        if not self.running:
            raise KeyboardInterrupt("User requested stop")


state = RuntimeState()
