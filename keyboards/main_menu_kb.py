from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon.lexicon import LEXICON_RU

def get_main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(text=LEXICON_RU["menu.buy"])
    builder.button(text=LEXICON_RU["menu.informations"])

    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)