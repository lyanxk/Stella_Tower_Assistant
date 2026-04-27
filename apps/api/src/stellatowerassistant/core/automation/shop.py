from __future__ import annotations

import time

from ..config.settings import (
    FINAL_SHOP_REFRESH_LIMIT,
    HUNDRED_MATCH_THRESHOLD,
    IMAGE_MATCH_THRESHOLD,
    SELECT_CONFIRM_TIMEOUT,
    SELECT_MATCH_THRESHOLD,
    SHOP_BUBBLE_X_OFFSET,
    SHOP_BUBBLE_Y_FACTORS,
    SOLD_OUT_FILTER_DISTANCE,
    SOLD_OUT_MATCH_THRESHOLD,
    THUMB_REWARD_TIMEOUT,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .actions import click_blank, click_match_center, click_relative
from .readings import observe_run_reading
from .vision import Point, capture_emulator, find_all_matches, load_template, match_template


def handle_shop(final_shop: bool = False) -> None:
    click_bubble(1)
    take_thumb_reward()
    time.sleep(1.0)

    click_bubble(1)
    take_thumb_reward()
    time.sleep(1.0)

    click_bubble(0)
    purchase_items()
    time.sleep(1.0)

    if final_shop:
        handle_final_shop_refreshes()
    else:
        exit_regular_shop()

    click_bubble(2)
    if final_shop:
        confirm_final_shop_exit()


def click_bubble(index: int) -> None:
    _, window_rect = capture_emulator()
    bubble_y = int(window_rect[3] * SHOP_BUBBLE_Y_FACTORS[index])
    click_relative(SHOP_BUBBLE_X_OFFSET, bubble_y, window_rect, delay=0.8)


def purchase_items() -> None:
    purchase_note_items()
    purchase_hundred_items()


def purchase_note_items() -> None:
    note_template = load_template("note")
    if note_template is None:
        return

    while True:
        state.check_pause_and_running()
        image, _ = capture_emulator()
        observe_run_reading(image)
        available_notes = find_available_positions(image, note_template, IMAGE_MATCH_THRESHOLD)
        if not available_notes:
            break

        bought_any = False
        for match in available_notes:
            _, window_rect = capture_emulator()
            click_match_center(match, window_rect, delay=0.25)

            if not click_buy_button(delay=0.35):
                continue

            dialog_rect = click_confirm_if_present(delay=0.2)
            click_blank(dialog_rect, times=20, delay=0.05)
            bought_any = True
            break

        if not bought_any:
            emit_log("debug: no more purchasable notes found, breaking out of loop", scope="shop")
            break

        time.sleep(0.2)


def purchase_hundred_items() -> None:
    hundred_template = load_template("hundred")
    if hundred_template is None:
        return

    while True:
        state.check_pause_and_running()
        image, _ = capture_emulator()
        observe_run_reading(image)
        available_hundreds = find_available_positions(image, hundred_template, HUNDRED_MATCH_THRESHOLD)
        if not available_hundreds:
            emit_log("debug: no more purchasable 100s found, breaking out of loop", scope="shop")
            break

        bought_one = False
        for match in available_hundreds:
            _, window_rect = capture_emulator()
            click_match_center(match, window_rect, delay=0.3)

            if not click_buy_button(delay=0.4):
                continue

            dialog_rect = click_confirm_if_present(delay=0.2)
            click_blank(dialog_rect, times=3)
            time.sleep(0.8)
            take_thumb_reward()
            bought_one = True
            break

        if not bought_one:
            emit_log("debug: found 100s but none could be bought (no buy button), breaking to avoid loop", scope="shop")
            break

        time.sleep(0.2)


def take_thumb_reward(timeout: float = THUMB_REWARD_TIMEOUT) -> None:
    select_template = load_template("select")
    confirm_template = load_template("select_confirm")
    if select_template is None or confirm_template is None:
        return

    start_time = time.time()
    while time.time() - start_time < timeout:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        observe_run_reading(image)
        select_match = match_template(image, select_template, threshold=SELECT_MATCH_THRESHOLD)
        if not select_match:
            time.sleep(0.2)
            continue

        click_match_center(select_match, window_rect, delay=0.3)

        confirm_start = time.time()
        while time.time() - confirm_start < SELECT_CONFIRM_TIMEOUT:
            state.check_pause_and_running()
            confirm_image, confirm_rect = capture_emulator()
            confirm_match = match_template(confirm_image, confirm_template, threshold=SELECT_MATCH_THRESHOLD)
            if confirm_match:
                click_match_center(confirm_match, confirm_rect, delay=0.2)
                click_blank(confirm_rect)
                return
            time.sleep(0.2)
        return


def handle_final_shop_refreshes() -> None:
    refresh_template = load_template("refresh")
    back_template = load_template("back")
    if refresh_template is None:
        return

    refresh_count = 0
    while refresh_count < FINAL_SHOP_REFRESH_LIMIT:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        observe_run_reading(image)
        refresh_match = match_template(image, refresh_template, threshold=IMAGE_MATCH_THRESHOLD)
        if not refresh_match:
            break

        click_match_center(refresh_match, window_rect, delay=0.3)
        time.sleep(0.1)
        purchase_items()
        refresh_count += 1

    if refresh_count != FINAL_SHOP_REFRESH_LIMIT or back_template is None:
        return

    emit_log("debug: reached final shop refresh limit, exiting shop", scope="shop")
    image, window_rect = capture_emulator()
    observe_run_reading(image)
    back_match = match_template(image, back_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not back_match:
        return

    click_blank(window_rect)
    click_match_center(back_match, window_rect, delay=0.5)
    emit_log("debug: quit shop after refresh limit", scope="shop")


def exit_regular_shop() -> None:
    emit_log("Purchase process completed. Checking whether the shop can be closed...", scope="shop")
    back_template = load_template("back")
    if back_template is None:
        return

    image, window_rect = capture_emulator()
    observe_run_reading(image)
    back_match = match_template(image, back_template, threshold=IMAGE_MATCH_THRESHOLD)
    if back_match:
        click_match_center(back_match, window_rect, delay=0.5)
        emit_log("debug: quit shop", scope="shop")
        return

    emit_log("debug: no back button found, pause", level="warning", scope="shop")
    state.toggle_pause()


def confirm_final_shop_exit() -> None:
    emit_log("debug: final shop - checking for confirm button", scope="shop")
    confirm_template = load_template("confirm")
    if confirm_template is None:
        return

    image, window_rect = capture_emulator()
    observe_run_reading(image)
    confirm_match = match_template(image, confirm_template, threshold=IMAGE_MATCH_THRESHOLD)
    if confirm_match:
        click_match_center(confirm_match, window_rect, delay=0.5)


def click_buy_button(delay: float) -> bool:
    buy_template = load_template("buy")
    if buy_template is None:
        return False

    image, window_rect = capture_emulator()
    observe_run_reading(image)
    buy_match = match_template(image, buy_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not buy_match:
        return False

    click_match_center(buy_match, window_rect, delay=delay)
    return True


def click_confirm_if_present(delay: float) -> tuple[int, int, int, int]:
    confirm_template = load_template("confirm")
    image, window_rect = capture_emulator()
    observe_run_reading(image)
    if confirm_template is None:
        return window_rect

    confirm_match = match_template(image, confirm_template, threshold=IMAGE_MATCH_THRESHOLD)
    if confirm_match:
        click_match_center(confirm_match, window_rect, delay=delay)
    return window_rect


def find_available_positions(image, item_template, threshold: float) -> list[Point]:
    item_matches = find_all_matches(image, item_template, threshold)
    if not item_matches:
        return []

    sold_out_template = load_template("sold_out")
    if sold_out_template is None:
        return item_matches

    sold_out_matches = find_all_matches(image, sold_out_template, SOLD_OUT_MATCH_THRESHOLD)
    return [match for match in item_matches if not is_near_any(match, sold_out_matches)]


def is_near_any(match: Point, other_matches: list[Point], distance: int = SOLD_OUT_FILTER_DISTANCE) -> bool:
    return any(abs(match[0] - other[0]) + abs(match[1] - other[1]) <= distance for other in other_matches)
