from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

def get_admin_confirmation_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=LEXICON_RU["admin.confirmation_yes"],
        callback_data=f"admin:approve:{order_id}",
    )
    builder.button(
        text=LEXICON_RU["admin.confirmation_no"],
        callback_data=f"admin:reject:{order_id}",
    )
    builder.adjust(2)

    return builder.as_markup()
