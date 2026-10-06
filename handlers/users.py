from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main_menu_kb import get_main_menu_kb

from lexicon.lexicon import LEXICON_RU

user_router = Router(name=__name__)

@user_router.message(CommandStart())
async def process_command_start(
    message: Message,
    state: FSMContext,
) -> None:
    await message.answer(
        text=LEXICON_RU["common.start"],
        reply_markup=get_main_menu_kb(),
    )
    await state.clear()

@user_router.message(Command(commands="help"))
async def process_command_help(
    message: Message,
) -> None:
    await message.answer(
        text=LEXICON_RU["common.help"]
    )
