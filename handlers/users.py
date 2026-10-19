import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message
from aiogram.fsm.context import FSMContext

from keyboards.main_menu_kb import get_main_menu_kb

from lexicon.lexicon import LEXICON_RU

user_router = Router(name=__name__)
logger = logging.getLogger(__name__)

OFFER_FILE_PATH = (
    Path(__file__).resolve().parent.parent
    / "documents"
    / "offer_agreement.pdf"
)

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

    if not OFFER_FILE_PATH.is_file():
        logger.warning("Offer agreement file not found: %s", OFFER_FILE_PATH)
        return

    await message.answer_document(
        document=FSInputFile(OFFER_FILE_PATH),
        caption=LEXICON_RU["common.offer_caption"],
    )

@user_router.message(Command(commands="help"))
async def process_command_help(
    message: Message,
) -> None:
    await message.answer(
        text=LEXICON_RU["common.help"]
    )


@user_router.message(F.text == LEXICON_RU["menu.informations"])
async def process_event_information(message: Message) -> None:
    await message.answer(text=LEXICON_RU["event.information"])
