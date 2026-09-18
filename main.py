import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import load_config

from handlers import routers

logger = logging.getLogger(__name__)

async def main() -> None:
    config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )
    logger.info("Starting bot")

    bot = Bot(
        token=config.bot.token
    )

    dp = Dispatcher()
    dp["config"] = config
    dp.include_routers(*routers)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())