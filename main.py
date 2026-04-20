from __future__ import annotations

import time

import keyboard

from actions import click_template_if_present, continuous_fast_click, select_choice_or_first, wait_and_click
from config import IMAGE_MATCH_THRESHOLD, MAX_RUNS, MAX_SHOPS_PER_RUN, SELECT_MATCH_THRESHOLD
from shop import handle_shop
from state import state
from vision import capture_emulator, load_template, match_template


def main_loop() -> None:
    print("Waiting for quick_start (press S to skip initial waits, P pause, Q quit)")
    wait_and_click("quick_start", timeout=60)

    print("Waiting for next")
    wait_and_click("next", timeout=60)

    print("Waiting for start_battle")
    wait_and_click("start_battle", timeout=60)

    state.reset_initial_wait()
    print("Entered tower run. Starting automation...")

    shop_counter = 0
    while True:
        state.check_pause_and_running()
        continuous_fast_click()
        image, window_rect = capture_emulator()

        if exit_run_if_save_found(image, window_rect):
            break

        if enter_shop_if_needed(image, shop_counter):
            shop_counter += 1
            continue

        if has_choice_prompt(image):
            select_choice_or_first()
            continue

        time.sleep(0.2)

    print("Automation complete.")


def run_automation() -> None:
    register_hotkeys()

    run_count = 0
    while state.running and run_count < MAX_RUNS:
        run_count += 1
        print(f"===== Run {run_count}/{MAX_RUNS} =====")

        try:
            main_loop()
            time.sleep(1.0)
        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as exc:
            print(f"Error: {exc}")
            time.sleep(2.0)
        finally:
            state.reset_initial_wait()

    print("All runs completed.")


def register_hotkeys() -> None:
    keyboard.add_hotkey("p", state.toggle_pause)
    keyboard.add_hotkey("s", state.mark_skip_initial)
    keyboard.add_hotkey("q", state.stop)
    print("Hotkeys: P=pause/resume, S=skip initial waits, Q=quit")


def exit_run_if_save_found(image, window_rect) -> bool:
    if not click_template_if_present(image, window_rect, "save", delay=0.5):
        return False

    print("Found save marker. Exiting run...")
    confirm_image, confirm_rect = capture_emulator()
    click_template_if_present(confirm_image, confirm_rect, "confirm", delay=1.5)
    return True


def enter_shop_if_needed(image, shop_counter: int) -> bool:
    enter_shop_template = load_template("enter_shop")
    if enter_shop_template is None or shop_counter >= MAX_SHOPS_PER_RUN:
        return False

    shop_match = match_template(image, enter_shop_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not shop_match:
        return False

    print(f"Encountered shop {shop_counter + 1}")
    final_shop = shop_counter == MAX_SHOPS_PER_RUN - 1
    handle_shop(final_shop=final_shop)
    return True


def has_choice_prompt(image) -> bool:
    select_template = load_template("select")
    choice_template = load_template("choice")

    select_match = match_template(image, select_template, threshold=SELECT_MATCH_THRESHOLD) if select_template is not None else None
    choice_match = match_template(image, choice_template, threshold=IMAGE_MATCH_THRESHOLD) if choice_template is not None else None

    if select_match or choice_match:
        print(f"[Debug] select_match={select_match}, choice_match={choice_match}")
        return True

    return False


if __name__ == "__main__":
    run_automation()
