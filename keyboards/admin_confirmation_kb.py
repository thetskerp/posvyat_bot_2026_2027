from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

def get_admin_confirmation_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=LEXICON_RU["admin.confirmations_yes"]
    )
    builder.button(
        text=LEXICON_RU["admin.confirmations_no"]
    )
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)