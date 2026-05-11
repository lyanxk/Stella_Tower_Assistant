from __future__ import annotations

import time

import keyboard

from ..config.settings import (
    FAST_CLICK_BURST_DURATION,
    FAST_CLICK_DURATION,
    IMAGE_MATCH_THRESHOLD,
    MAX_RUNS,
    MAX_SHOPS_PER_RUN,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .actions import click_template_if_present, continuous_fast_click, select_second_choice
from .potential import handle_potential_selection, has_potential_prompt
from .readings import reset_run_reading_observer
from .shop import handle_shop
from .vision import capture_emulator, find_all_matches, load_template, match_template

_HOTKEYS_REGISTERED = False


def main_loop() -> None:
    reset_run_reading_observer()
    run_start_sequence_until_tower_detected()
    emit_log("Entered tower run. Starting automation...", scope="automation")

    shop_counter = 0
    while True:
        handled, should_exit, shop_counter = inspect_current_screen(shop_counter)
        if should_exit:
            break
        if handled:
            continue

        _, should_exit, shop_counter = fast_click_with_interleaved_recognition(shop_counter)
        if should_exit:
            break

    emit_log("Automation complete.", scope="automation")


def run_automation() -> None:
    register_hotkeys()

    run_count = 0
    while state.running and run_count < MAX_RUNS:
        run_count += 1
        state.mark_run(run_count, MAX_RUNS)
        emit_log(f"===== Run {run_count}/{MAX_RUNS} =====", scope="automation")

        try:
            main_loop()
            time.sleep(1.0)
        except KeyboardInterrupt:
            emit_log("Stopped by user.", level="warning", scope="automation")
            break
        except Exception as exc:
            state.mark_error(str(exc))
            emit_log(f"Error: {exc}", level="error", scope="automation")
            time.sleep(2.0)

    emit_log("All runs completed.", scope="automation")


def register_hotkeys() -> None:
    global _HOTKEYS_REGISTERED
    if _HOTKEYS_REGISTERED:
        return

    keyboard.add_hotkey("p", state.toggle_pause)
    keyboard.add_hotkey("q", state.stop)
    _HOTKEYS_REGISTERED = True
    emit_log("Hotkeys: P=pause/resume, Q=quit", scope="runtime")


def exit_run_if_save_found(image, window_rect) -> bool:
    if not click_template_if_present(image, window_rect, "save", delay=0.5):
        return False

    emit_log("Found save marker. Exiting run...", scope="automation")
    confirm_image, confirm_rect = capture_emulator()
    click_template_if_present(confirm_image, confirm_rect, "confirm", delay=1.5)
    leave_image, leave_rect = capture_emulator()
    click_template_if_present(leave_image, leave_rect, "leave", delay=0.5)
    return True


def run_start_sequence_until_tower_detected() -> None:
    for template_name in ("quick_start", "next", "start_battle"):
        if wait_and_click_or_detect_tower(template_name, timeout=60):
            return

    wait_for_tower_template_after_start()


def wait_and_click_or_detect_tower(template_name: str, timeout: float) -> bool:
    emit_log(f"Waiting for {template_name} or tower UI templates", scope="automation")
    start_time = time.time()
    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        if is_tower_logic_visible(image):
            emit_log("Tower UI template detected. Entering tower logic.", scope="automation")
            return True

        if click_template_if_present(image, window_rect, template_name):
            return False

        time.sleep(0.5)

    emit_log(f"[Timeout] {template_name} not found in {timeout} seconds", level="warning", scope="automation")
    return False


def wait_for_tower_template_after_start() -> None:
    emit_log("Start clicked. Waiting for tower UI templates...", scope="automation")
    while True:
        state.check_pause_and_running()
        image, _ = capture_emulator()
        if is_tower_logic_visible(image):
            emit_log("Tower UI template detected. Entering tower logic.", scope="automation")
            return
        time.sleep(0.5)


def is_tower_logic_visible(image) -> bool:
    return find_first_template_match(image, ("select_confirm", "refresh", "choice", "select", "enter_shop", "shop", "save")) is not None


def inspect_current_screen(shop_counter: int) -> tuple[bool, bool, int]:
    state.check_pause_and_running()
    image, window_rect = capture_emulator()

    if exit_run_if_save_found(image, window_rect):
        return True, True, shop_counter

    if enter_shop_if_needed(image, shop_counter):
        return True, False, shop_counter + 1

    if select_second_choice_if_needed(image):
        return True, False, shop_counter

    if has_potential_prompt(image):
        handle_potential_selection()
        return True, False, shop_counter

    if click_template_if_present(image, window_rect, "enter", delay=0.5):
        return True, False, shop_counter

    return False, False, shop_counter


def fast_click_with_interleaved_recognition(shop_counter: int) -> tuple[bool, bool, int]:
    remaining_duration = FAST_CLICK_DURATION
    burst_duration = FAST_CLICK_BURST_DURATION if FAST_CLICK_BURST_DURATION > 0 else FAST_CLICK_DURATION

    while remaining_duration > 0:
        current_burst = min(burst_duration, remaining_duration)
        continuous_fast_click(duration=current_burst)
        remaining_duration = max(0.0, remaining_duration - current_burst)

        handled, should_exit, shop_counter = inspect_current_screen(shop_counter)
        if handled or should_exit:
            return handled, should_exit, shop_counter

    return False, False, shop_counter


def enter_shop_if_needed(image, shop_counter: int) -> bool:
    if shop_counter >= MAX_SHOPS_PER_RUN:
        return False

    shop_match = find_first_template_match(image, ("enter_shop", "shop"))
    if not shop_match:
        return False

    final_shop = has_template_match(image, "leave")
    shop_kind = "final shop" if final_shop else "regular shop"
    emit_log(f"Encountered {shop_kind} {shop_counter + 1}", scope="shop")
    handle_shop(final_shop=final_shop)
    return True


def find_first_template_match(image, template_names: tuple[str, ...]):
    for template_name in template_names:
        template = load_template(template_name)
        if template is None:
            continue

        match = match_template(image, template, threshold=IMAGE_MATCH_THRESHOLD)
        if match:
            emit_log(f"[Debug] {template_name} matched at {match}", scope="automation")
            return match

    return None


def has_template_match(image, template_name: str) -> bool:
    template = load_template(template_name)
    if template is None:
        return False

    return match_template(image, template, threshold=IMAGE_MATCH_THRESHOLD) is not None


def select_second_choice_if_needed(image) -> bool:
    choice_template = load_template("choice")
    if choice_template is None:
        return False

    choice_matches = find_all_matches(image, choice_template, IMAGE_MATCH_THRESHOLD)
    if not choice_matches:
        return False

    emit_log(f"Choice page detected with {len(choice_matches)} option marker(s). Selecting second option.", scope="automation")
    select_second_choice()
    wait_for_potential_after_choice()
    return True


def wait_for_potential_after_choice(timeout: float = 3.0) -> None:
    start_time = time.time()
    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        image, _ = capture_emulator()
        if has_potential_prompt(image):
            handle_potential_selection()
            return
        time.sleep(0.2)


if __name__ == "__main__":
    run_automation()
