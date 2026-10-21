import re
import logging
from datetime import date, datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext

from database import get_active_order_by_telegram_id
from handlers.states import BotStates

from keyboards.main_menu_kb import get_main_menu_kb
from keyboards.user_confirmation_kb import get_user_confirmation_kb, get_user_buy_confirmation_kb

from lexicon.lexicon import LEXICON_RU
form_router = Router()
logger = logging.getLogger(__name__)

OFFER_FILE_PATH = (
    Path(__file__).resolve().parent.parent
    / "documents"
    / "offer_agreement.pdf"
)

@form_router.message(F.text == LEXICON_RU["menu.buy"])
async def process_buy_button(
    message: Message,
    state: FSMContext,
):
    active_order = get_active_order_by_telegram_id(message.from_user.id)
    if active_order is not None:
        text_key = (
            "payment.active_approved"
            if active_order.status == "approved"
            else "payment.active_pending"
        )
        await message.answer(text=LEXICON_RU[text_key])
        return

    await message.answer(
        text=LEXICON_RU["form.name"]
    )
    await state.set_state(BotStates.waiting_for_name)

@form_router.message(BotStates.waiting_for_name)
async def process_get_full_name(
    message: Message,
    state: FSMContext,
):
    if message.text is None:
        await message.answer(text=LEXICON_RU["form.text_error"])
        return

    await state.update_data(full_name=message.text)
    await message.answer(text=LEXICON_RU["form.b_day"])
    await state.set_state(BotStates.waiting_for_date_birthday)

@form_router.message(BotStates.waiting_for_date_birthday)
async def process_get_birthday_date(
    message: Message,
    state: FSMContext,
):
    b_day_text = message.text

    if b_day_text is None or not re.fullmatch(
        r"\d{2}\.\d{2}\.\d{4}",
        b_day_text,
    ):
        await message.answer(text=LEXICON_RU["form.b_day_error"])
        return

    try:
        birthday = datetime.strptime(b_day_text, "%d.%m.%Y").date()
        today = date.today()
        age = (
            today.year
            - birthday.year
            - ((today.month, today.day) < (birthday.month, birthday.day))
        )
        if age < 18:
            await message.answer(text=LEXICON_RU["form.b_day_less_than_18"])
            await message.answer(
                text=LEXICON_RU["common.start"],
                reply_markup=get_main_menu_kb(),
            )
            await state.clear()
            return

    except ValueError:
        await message.answer(text=LEXICON_RU["form.b_day_invalid"])
        return

    await state.update_data(birthdate=b_day_text)
    await message.answer(text=LEXICON_RU["form.group"])
    await state.set_state(BotStates.waiting_for_group)

@form_router.message(BotStates.waiting_for_group)
async def process_get_group(
    message: Message,
    state: FSMContext,
):
    if message.text is None:
        await message.answer(text=LEXICON_RU["form.text_error"])
        return

    await state.update_data(group=message.text)

    data = await state.get_data()

    text = LEXICON_RU["form.check_data"].format(
        full_name=data["full_name"],
        birthdate=data["birthdate"],
        group=data["group"],
    )

    await state.set_state(BotStates.waiting_for_confirmation_from_user)
    await message.answer(
        text=text,
        reply_markup=get_user_confirmation_kb(),
    )

@form_router.callback_query(
    BotStates.waiting_for_confirmation_from_user,
    F.data == "form:confirm",
)
async def process_form_confirm(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.set_state(BotStates.waiting_for_payment)

    if not OFFER_FILE_PATH.is_file():
        logger.warning("Offer agreement file not found: %s", OFFER_FILE_PATH)
    else:
        await callback.message.answer_document(
            document=FSInputFile(OFFER_FILE_PATH),
            caption=LEXICON_RU["common.offer_caption"],
        )

    await callback.message.answer(
        text=LEXICON_RU["payment.details"],
        reply_markup=get_user_buy_confirmation_kb(),
    )

@form_router.callback_query(
    BotStates.waiting_for_confirmation_from_user,
    F.data == "form:edit",
)
async def process_form_edit(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)

    await state.set_state(BotStates.waiting_for_name)
    await callback.message.answer(text=LEXICON_RU["form.name"])

@form_router.callback_query(
    BotStates.waiting_for_confirmation_from_user,
    F.data == "form:cancel",
)
async def process_form_cancel(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()

    await callback.message.answer(
        text=LEXICON_RU["form.cancelled"],
        reply_markup=get_main_menu_kb(),
    )
