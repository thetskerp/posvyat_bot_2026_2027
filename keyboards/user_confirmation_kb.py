from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

def get_user_confirmation_kb() -> InlineKeyboardMarkup:
    builder_form = InlineKeyboardBuilder()

    builder_form.button(
        text=LEXICON_RU["user.confirmation_yes"],
        callback_data="form:confirm"
    )
    builder_form.button(
        text=LEXICON_RU["user.confirmation_no"],
        callback_data="form:edit"
    )
    builder_form.button(
        text=LEXICON_RU["user.confirmation_cancel"],
        callback_data="form:cancel"
    )
    builder_form.adjust(1)

    return builder_form.as_markup()

def get_user_buy_confirmation_kb() -> InlineKeyboardMarkup:
    builder_accept = InlineKeyboardBuilder()

    builder_accept.button(
        text=LEXICON_RU["user.buy_confirmation"],
        callback_data="payment:paid"
    )

    builder_accept.adjust(1)

    return builder_accept.as_markup()
