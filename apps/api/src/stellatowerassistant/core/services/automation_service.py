from __future__ import annotations

from threading import Lock, Thread

from ..automation.run_loop import run_automation
from ..config.settings import MAX_RUNS
from ..runtime.events import emit_log, event_store
from ..runtime.state import state


class AutomationService:
    def __init__(self) -> None:
        self._thread: Thread | None = None
        self._lock = Lock()

    def start(self) -> tuple[bool, str]:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False, "Automation is already running."

            state.reset_for_start(MAX_RUNS)
            self._thread = Thread(target=self._run_worker, name="automation-worker", daemon=True)
            self._thread.start()

        emit_log("Automation worker started.", scope="service", event_type="status")
        return True, "Automation started."

    def pause(self) -> tuple[bool, str]:
        if not self._thread_alive() or state.paused:
            return False, "Automation is not running or already paused."

        state.toggle_pause()
        return True, "Automation paused."

    def resume(self) -> tuple[bool, str]:
        if not self._thread_alive() or not state.paused:
            return False, "Automation is not paused."

        state.toggle_pause()
        return True, "Automation resumed."

    def stop(self) -> tuple[bool, str]:
        if not self._thread_alive():
            state.mark_finished("Automation idle")
            return False, "Automation is not running."

        state.stop()
        return True, "Stop requested."

    def skip_initial_wait(self) -> tuple[bool, str]:
        if not self._thread_alive():
            return False, "Automation is not running."

        state.mark_skip_initial()
        return True, "Initial waits will be skipped."

    def get_status(self) -> dict[str, object]:
        return state.snapshot(thread_alive=self._thread_alive())

    def get_logs(self, limit: int = 100) -> list[dict[str, object]]:
        return [event.asdict() for event in event_store.recent(limit)]

    def _run_worker(self) -> None:
        try:
            run_automation()
        except Exception as exc:
            state.mark_error(str(exc))
            emit_log(f"Automation worker crashed: {exc}", level="error", scope="service")
        finally:
            if state.last_error:
                state.mark_finished("Automation stopped with errors")
            elif state.last_message == "Stop requested":
                state.mark_finished("Automation stopped")
            else:
                state.mark_finished("Automation finished")

            emit_log(state.last_message, scope="service", event_type="status")

    def _thread_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()


automation_service = AutomationService()
