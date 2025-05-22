# src/bot/handlers/__init__.py
from .common import router as common_router
from .menu import router as menu_router
from .payment import router as payment_router
from .server import router as server_router # Import server router

__all__ = [
    "common_router",
    "menu_router",
    "payment_router",
    "server_router", # Add to __all__
]
