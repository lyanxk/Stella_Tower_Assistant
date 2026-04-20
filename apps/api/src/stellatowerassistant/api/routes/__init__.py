from .automation import router as automation_router
from .emulator import router as emulator_router
from .health import router as health_router
from .settings import router as settings_router
from .templates import router as templates_router

__all__ = [
    "automation_router",
    "emulator_router",
    "health_router",
    "settings_router",
    "templates_router",
]
