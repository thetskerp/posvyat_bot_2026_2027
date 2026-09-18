"""Telegram handlears"""

from handlers.users import user_router
from handlers.form_handlers import form_router

routers = (
    user_router,
    form_router,
)

__all__ = ["routers"]