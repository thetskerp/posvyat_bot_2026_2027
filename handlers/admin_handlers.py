import logging
from datetime import date

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config.config import Config
from database import get_order, list_approved_orders, update_order_status
from lexicon.lexicon import LEXICON_RU
from services import build_buyers_excel


admin_router = Router(name=__name__)
logger = logging.getLogger(__name__)


def _get_order_id(callback_data: str | None) -> int | None:
    if callback_data is None:
        return None

    try:
        return int(callback_data.rsplit(":", maxsplit=1)[1])
    except (IndexError, ValueError):
        return None


def _is_admin(user_id: int, config: Config) -> bool:
    return user_id in config.admins.ids


@admin_router.callback_query(F.data.startswith("admin:approve:"))
async def process_admin_approve(
    callback: CallbackQuery,
    bot: Bot,
    config: Config,
):
    if not _is_admin(callback.from_user.id, config):
        await callback.answer(
            text=LEXICON_RU["admin.access_denied"],
            show_alert=True,
        )
        return

    order_id = _get_order_id(callback.data)
    order = get_order(order_id) if order_id is not None else None
    if order is None:
        await callback.answer(
            text=LEXICON_RU["admin.order_not_found"],
            show_alert=True,
        )
        return

    if not update_order_status(
        order_id=order.id,
        status="approved",
        reviewed_by=callback.from_user.id,
    ):
        await callback.answer(
            text=LEXICON_RU["admin.order_already_reviewed"],
            show_alert=True,
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text=LEXICON_RU["admin.order_approved"].format(order_id=order.id)
    )

    try:
        await bot.send_message(
            chat_id=order.telegram_id,
            text=LEXICON_RU["payment.approved"],
        )
    except TelegramAPIError:
        logger.exception(
            "Failed to notify user %s about approved order %s",
            order.telegram_id,
            order.id,
        )


@admin_router.callback_query(F.data.startswith("admin:reject:"))
async def process_admin_reject(
    callback: CallbackQuery,
    bot: Bot,
    config: Config,
):
    if not _is_admin(callback.from_user.id, config):
        await callback.answer(
            text=LEXICON_RU["admin.access_denied"],
            show_alert=True,
        )
        return

    order_id = _get_order_id(callback.data)
    order = get_order(order_id) if order_id is not None else None
    if order is None:
        await callback.answer(
            text=LEXICON_RU["admin.order_not_found"],
            show_alert=True,
        )
        return

    if not update_order_status(
        order_id=order.id,
        status="rejected",
        reviewed_by=callback.from_user.id,
    ):
        await callback.answer(
            text=LEXICON_RU["admin.order_already_reviewed"],
            show_alert=True,
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        text=LEXICON_RU["admin.order_rejected"].format(order_id=order.id)
    )

    try:
        await bot.send_message(
            chat_id=order.telegram_id,
            text=LEXICON_RU["payment.rejected"].format(
                admin_contact=config.admins.contact,
            ),
        )
    except TelegramAPIError:
        logger.exception(
            "Failed to notify user %s about rejected order %s",
            order.telegram_id,
            order.id,
        )


@admin_router.message(Command("buyers"))
async def process_buyers_command(
    message: Message,
    config: Config,
):
    if message.from_user is None or not _is_admin(message.from_user.id, config):
        await message.answer(text=LEXICON_RU["admin.access_denied"])
        return

    orders = list_approved_orders()
    if not orders:
        await message.answer(text=LEXICON_RU["admin.buyers_empty"])
        return

    excel_file = BufferedInputFile(
        build_buyers_excel(orders),
        filename=f"buyers_{date.today().isoformat()}.xlsx",
    )
    await message.answer_document(
        document=excel_file,
        caption=LEXICON_RU["admin.buyers_caption"].format(
            buyers_count=len(orders),
        ),
    )
