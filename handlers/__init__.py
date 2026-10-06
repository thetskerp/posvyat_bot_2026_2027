"""Telegram handlears"""

from handlers.users import user_router
from handlers.form_handlers import form_router
from handlers.payment_handlers import payment_router
from handlers.admin_handlers import admin_router

routers = (
    user_router,
    form_router,
    payment_router,
    admin_router,
)

__all__ = ["routers"]
