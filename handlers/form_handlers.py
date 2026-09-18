import re
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext

from handlers.states import BotStates

from keyboards.main_menu_kb import get_main_menu_kb
from keyboards.user_confirmation_kb import get_user_confirmation_kb, get_user_buy_confirmation_kb

from lexicon.lexicon import LEXICON_RU
form_router = Router()

@form_router.message(F.text == LEXICON_RU["menu.buy"])
async def process_buy_button(
    message: Message,
    state: FSMContext,
):
    await message.answer(
        text=LEXICON_RU["form.name"]
    )
    await state.set_state(BotStates.waiting_for_name)

@form_router.message(BotStates.waiting_for_name)
async def process_get_full_name(
    message: Message,
    state: FSMContext,
):
    await state.update_data(full_name=message.text)
    await message.answer(text=LEXICON_RU["form.b_day"])
    await state.set_state(BotStates.waiting_for_date_birthday)

@form_router.message(BotStates.waiting_for_date_birthday)
async def process_get_birthday_date(
    message: Message,
    state: FSMContext,
):
    b_day_text = message.text

    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", b_day_text):
        await message.answer(text=LEXICON_RU["form.b_day_error"])
        return

    try:
        birthday = datetime.strptime(b_day_text, "%d.%m.%Y")
        age = (datetime.now() - birthday).days // 365
        if age < 18:
            await message.answer(text=LEXICON_RU["form.b_day_less_than_18"])
            await message.answer(
                text=LEXICON_RU["common.start"],
                reply_markup=get_main_menu_kb(),
            )
            return

    except ValueError:
        await message.answer(text="Ошибка: Введена некорректная дата.")
        return

    await state.update_data(birthdate=b_day_text)
    await message.answer(text=LEXICON_RU["form.group"])
    await state.set_state(BotStates.waiting_for_group)

@form_router.message(BotStates.waiting_for_group)
async def process_get_group(
    message: Message,
    state: FSMContext,
):
    await state.update_data(group=message.text)

    data = await state.get_data()

    text = (
        "Проверьте введённые данные:\n\n"
        f"ФИО: {data['full_name']}\n"
        f"Дата рождения: {data['birthdate']}\n"
        f"Группа/вуз: {data['group']}"
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
        text="Покупка отменена",
        reply_markup=get_main_menu_kb(),
    )
