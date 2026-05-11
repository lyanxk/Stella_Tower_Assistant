from __future__ import annotations

import time

from ..config.settings import (
    FINAL_SHOP_ITEM_TEMPLATES,
    HUNDRED_MATCH_THRESHOLD,
    IMAGE_MATCH_THRESHOLD,
    REGULAR_SHOP_ITEM_TEMPLATES,
    SHOP_BUBBLE_X_OFFSET,
    SHOP_BUBBLE_Y_FACTORS,
    SHOP_EXTRA_UPGRADE_LIMIT,
    SHOP_REFRESH_LIMIT,
    SHOP_UPGRADE_TIMES,
    SOLD_OUT_FILTER_DISTANCE,
    SOLD_OUT_MATCH_THRESHOLD,
)
from ..runtime.events import emit_log
from ..runtime.state import state
from .actions import click_blank, click_match_center, click_relative
from .potential import handle_potential_selection
from .readings import observe_run_reading
from .vision import Point, capture_emulator, find_all_matches, load_template, match_template


def handle_shop(final_shop: bool = False) -> None:
    if final_shop:
        emit_log("Handling final shop flow.", scope="shop")
        handle_final_shop()
        return

    emit_log("Handling regular shop flow.", scope="shop")
    handle_regular_shop()


def handle_regular_shop() -> None:
    open_purchase_page()
    purchase_items(REGULAR_SHOP_ITEM_TEMPLATES)
    quit_shopping()
    upgrade_times(SHOP_UPGRADE_TIMES)
    exit_shop()


def quit_shopping() -> None:
    back_template = load_template("back")
    if back_template is None:
        emit_log("Back template not found; cannot quit shopping page.", level="warning", scope="shop")
        return

    start_time = time.time()
    while time.time() - start_time < 8.0:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        observe_run_reading(image)

        if is_shop_layer(image):
            emit_log("Returned to shop layer.", scope="shop")
            return

        back_match = match_template(image, back_template, threshold=IMAGE_MATCH_THRESHOLD)
        if back_match:
            if not is_shopping_page(image):
                emit_log("Back marker found outside shopping page; leaving it untouched.", scope="shop")
                return

            click_match_center(back_match, window_rect, delay=0.5)
            continue

        time.sleep(0.2)

    emit_log("Timed out while waiting to return to shop layer.", level="warning", scope="shop")


def handle_final_shop() -> None:
    upgrade_times(SHOP_UPGRADE_TIMES)
    open_purchase_page()

    for refresh_round in range(SHOP_REFRESH_LIMIT + 1):
        purchase_items(FINAL_SHOP_ITEM_TEMPLATES)
        if refresh_round >= SHOP_REFRESH_LIMIT:
            break
        if not refresh_shop():
            break

    quit_shopping()
    upgrade_until_no_money()
    exit_shop(confirm_exit=True)


def open_purchase_page() -> None:
    click_bubble(0)


def click_bubble(index: int) -> None:
    _, window_rect = capture_emulator()
    bubble_y = int(window_rect[3] * SHOP_BUBBLE_Y_FACTORS[index])
    click_relative(SHOP_BUBBLE_X_OFFSET, bubble_y, window_rect, delay=0.8)


def purchase_items(template_names: tuple[str, ...]) -> int:
    bought_count = 0
    for template_name in template_names:
        bought_count += purchase_item_type(template_name)
    return bought_count


def purchase_item_type(template_name: str) -> int:
    item_template = load_template(template_name)
    if item_template is None:
        return 0

    threshold = _threshold_for_item(template_name)
    bought_count = 0

    while True:
        state.check_pause_and_running()
        image, window_rect = capture_emulator()
        available_items = find_available_positions(image, item_template, threshold)
        if not available_items:
            break

        bought_one = False
        for match in available_items:
            click_match_center(match, window_rect)
            if not click_buy_button():
                if handle_not_enough_money():
                    return bought_count
                click_blank(window_rect)
                continue

            if handle_not_enough_money():
                return bought_count
            click_confirm_if_present(delay=0.2)
            if handle_not_enough_money():
                return bought_count
            handle_potential_selection()
            bought_count += 1
            bought_one = True
            break

        if not bought_one:
            break

        time.sleep(0.2)

    if bought_count:
        emit_log(f"Bought {bought_count} item(s) for template {template_name}.", scope="shop")
    return bought_count


def upgrade_times(times: int) -> None:
    for index in range(times):
        state.check_pause_and_running()
        emit_log(f"Shop upgrade {index + 1}/{times}", scope="shop")
        open_upgrade_page()
        if handle_not_enough_money():
            return
        handle_potential_selection()
        time.sleep(0.3)


def upgrade_until_no_money(limit: int = SHOP_EXTRA_UPGRADE_LIMIT) -> None:
    for index in range(limit):
        state.check_pause_and_running()
        emit_log(f"Final shop extra upgrade attempt {index + 1}", scope="shop")
        open_upgrade_page()
        if handle_not_enough_money():
            emit_log("No enough money for more upgrades.", scope="shop")
            return
        if not handle_potential_selection(timeout=4.0):
            emit_log("No potential prompt after upgrade, stopping extra upgrades.", scope="shop")
            return
        time.sleep(0.3)


def refresh_shop() -> bool:
    image, window_rect = capture_emulator()
    refresh_template = load_template("refresh")
    refresh_match = match_template(image, refresh_template, threshold=IMAGE_MATCH_THRESHOLD) if refresh_template is not None else None
    if not refresh_match:
        return False

    emit_log("Refreshing final shop.", scope="shop")
    click_match_center(refresh_match, window_rect, delay=0.5)
    return True


def exit_shop(confirm_exit: bool = False) -> None:
    emit_log("Exiting shop.", scope="shop")
    if not click_back_if_present():
        click_bubble(2)
    if confirm_exit:
        confirm_exit_if_present()


def open_upgrade_page() -> None:
    image, window_rect = capture_emulator()
    observe_run_reading(image)
    strengthen_template = load_template("strengthen")
    strengthen_match = (
        match_template(image, strengthen_template, threshold=IMAGE_MATCH_THRESHOLD)
        if strengthen_template is not None
        else None
    )
    if strengthen_match:
        click_match_center(strengthen_match, window_rect, delay=0.5)
        return

    click_bubble(1)


def click_back_if_present() -> bool:
    back_template = load_template("back")
    if back_template is None:
        return False

    image, window_rect = capture_emulator()
    observe_run_reading(image)
    if not is_shopping_page(image):
        return False

    back_match = match_template(image, back_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not back_match:
        return False

    click_blank(window_rect)
    click_match_center(back_match, window_rect, delay=0.5)
    return True


def is_shop_layer(image) -> bool:
    for template_name in ("enter_shop", "strengthen", "leave", "shop"):
        template = load_template(template_name)
        if template is None:
            continue
        if match_template(image, template, threshold=IMAGE_MATCH_THRESHOLD):
            return True
    return False


def is_shopping_page(image) -> bool:
    shopping_template_names = (
        *REGULAR_SHOP_ITEM_TEMPLATES,
        *FINAL_SHOP_ITEM_TEMPLATES,
        "buy",
        "sold_out",
        "not_enough_money",
    )
    for template_name in dict.fromkeys(shopping_template_names):
        template = load_template(template_name)
        if template is None:
            continue
        if match_template(image, template, threshold=_threshold_for_item(template_name)):
            return True
    return False


def click_buy_button() -> bool:
    buy_template = load_template("buy")
    if buy_template is None:
        return False

    image, window_rect = capture_emulator()
    buy_match = match_template(image, buy_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not buy_match:
        return False

    click_match_center(buy_match, window_rect)
    return True


def click_confirm_if_present(delay: float) -> bool:
    confirm_template = load_template("confirm")
    image, window_rect = capture_emulator()
    observe_run_reading(image)
    if confirm_template is None:
        return False

    confirm_match = match_template(image, confirm_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not confirm_match:
        return False

    click_match_center(confirm_match, window_rect, delay=delay)
    return True


def confirm_exit_if_present() -> None:
    click_confirm_if_present(delay=0.5)


def handle_not_enough_money() -> bool:
    not_enough_template = load_template("not_enough_money")
    if not_enough_template is None:
        return False

    image, window_rect = capture_emulator()
    observe_run_reading(image)
    not_enough_match = match_template(image, not_enough_template, threshold=IMAGE_MATCH_THRESHOLD)
    if not not_enough_match:
        return False

    emit_log("Not enough money prompt detected.", scope="shop")
    click_confirm_if_present(delay=0.2)
    click_blank(window_rect)
    return True


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


def _threshold_for_item(template_name: str) -> float:
    if template_name == "hundred":
        return HUNDRED_MATCH_THRESHOLD
    return IMAGE_MATCH_THRESHOLD
