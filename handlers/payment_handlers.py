import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config.config import Config
from database import ActiveOrderExistsError, create_order, get_active_order_by_telegram_id
from handlers.states import BotStates
from keyboards.admin_confirmation_kb import get_admin_confirmation_kb
from lexicon.lexicon import LEXICON_RU


payment_router = Router(name=__name__)
logger = logging.getLogger(__name__)


@payment_router.callback_query(
    BotStates.waiting_for_payment,
    F.data == "payment:paid",
)
async def process_payment_paid(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    config: Config,
):
    await callback.answer()

    active_order = get_active_order_by_telegram_id(callback.from_user.id)
    if active_order is not None:
        text_key = (
            "payment.active_approved"
            if active_order.status == "approved"
            else "payment.active_pending"
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=LEXICON_RU[text_key])
        await state.clear()
        return

    data = await state.get_data()

    try:
        order = create_order(
            telegram_id=callback.from_user.id,
            telegram_username=callback.from_user.username,
            full_name=data["full_name"],
            birthdate=data["birthdate"],
            group_name=data["group"],
        )
    except ActiveOrderExistsError:
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(text=LEXICON_RU["payment.active_pending"])
        await state.clear()
        return

    username = (
        f"@{order.telegram_username}"
        if order.telegram_username
        else "не указан"
    )
    admin_text = LEXICON_RU["admin.new_order"].format(
        order_id=order.id,
        full_name=order.full_name,
        birthdate=order.birthdate,
        group_name=order.group_name,
        username=username,
        telegram_id=order.telegram_id,
    )

    for admin_id in config.admins.ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                reply_markup=get_admin_confirmation_kb(order.id),
            )
        except TelegramAPIError:
            logger.exception(
                "Failed to send order %s to admin %s",
                order.id,
                admin_id,
            )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text=LEXICON_RU["payment.sent"])
    await state.clear()
