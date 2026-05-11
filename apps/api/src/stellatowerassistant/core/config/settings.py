from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[4]
SRC_DIR = APP_DIR / "src"
PACKAGE_DIR = SRC_DIR / "stellatowerassistant"
ASSET_DIR = APP_DIR / "assets"
RESOURCE_DIR = ASSET_DIR / "templates"

API_HOST = "127.0.0.1"
API_PORT = 8765
CORS_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)
LOG_HISTORY_LIMIT = 300

EMULATOR_TITLE_KEYWORDS = ("mumu",)

IMAGE_MATCH_THRESHOLD = 0.80
SELECT_MATCH_THRESHOLD = 0.70
HUNDRED_MATCH_THRESHOLD = 0.90
SOLD_OUT_MATCH_THRESHOLD = 0.80

MATCH_POLL_INTERVAL = 0.2
PAUSE_POLL_INTERVAL = 0.1
SELECT_CONFIRM_TIMEOUT = 3.0
THUMB_REWARD_TIMEOUT = 6.0

FAST_CLICK_DELAY = 0.05
FAST_CLICK_DURATION = 1.5
FAST_CLICK_BURST_DURATION = 0.12
FAST_CLICK_X_OFFSET = 10
BLANK_CLICK_X_OFFSET = 10
FALLBACK_CHOICE_X_RATIO = 0.20
FALLBACK_SECOND_CHOICE_Y_RATIO = 0.60

SHOP_BUBBLE_X_OFFSET = 500
SHOP_BUBBLE_Y_FACTORS = (0.40, 0.60, 0.75)
MATCH_DEDUP_DISTANCE = 20
SOLD_OUT_FILTER_DISTANCE = 150
POTENTIAL_REFRESH_LIMIT = 2
POTENTIAL_REFRESH_WAIT_SECONDS = 1.0
SHOP_REFRESH_LIMIT = 2
SHOP_UPGRADE_TIMES = 3
SHOP_EXTRA_UPGRADE_LIMIT = 20
REGULAR_SHOP_ITEM_TEMPLATES = ("hundred", "one_sixty")
FINAL_SHOP_ITEM_TEMPLATES = ("hundred", "one_sixty", "tag")

MAX_SHOPS_PER_RUN = 4
MAX_RUNS = 7

OCR_OBSERVE_INTERVAL = 0.25
OCR_CURRENT_GOLD_THRESHOLD = 0.80
OCR_CURRENT_GOLD_FALLBACK_THRESHOLD = 0.60
# OCR regions are ratios of the full Windows emulator window screenshot,
# including the title bar. Reference screenshots: 1275x757.
OCR_CURRENT_GOLD_REGION = (0.887059, 0.062087, 0.098039, 0.067371)

TEMPLATES = {
    "quick_start": "quick_start_button.png",
    "next": "next.png",
    "start_battle": "start_battle.png",
    "choice": "choice.png",
    "tag": "tag.png",
    "note": "note.png",
    "hundred": "100.png",
    "one_sixty": "160.png",
    "buy": "buy.png",
    "refresh": "refresh.png",
    "back": "back.png",
    "leave": "leave.png",
    "save": "save.png",
    "enter_shop": "enter_shop.png",
    "not_enough_money": "not_enough_money.png",
    "enter": "enter_button.png",
    "confirm": "confirm.png",
    "select": "select.png",
    "select_confirm": "select_confirm.png",
    "shop": "shop.png",
    "strengthen": "strengthen.png",
    "sold_out": "sold_out.png",
}
