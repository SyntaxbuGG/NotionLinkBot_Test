import asyncio
import logging

import orjson

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.logging.logger_setup import setup_logging
from tgbot.handlers.commands import router
from tgbot.handlers.working_db import db_router
from tgbot.data import config
from tgbot.database.sqlalchemydb import engine


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    try:
        # Отправляем сообщение о завершении работы
        await bot.send_message(
            chat_id=config.CHAT_ID, text="🔴 <code><b>BOT STOPPED</b></code>"
        )
    except Exception as e:
        print(f"Failed to send shutdown message to Telegram: {e}")
    finally:
        await bot.session.close()
        await dispatcher.storage.close()
        await engine.dispose()


async def main():
    session = AiohttpSession(
        json_loads=orjson.loads,
    )
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = MemoryStorage()
    setup_logging(bot=bot, chat_id=config.CHAT_ID)
    dp = Dispatcher(
        storage=storage,
    )
    dp.include_routers(router, db_router)

    dp.shutdown.register(aiogram_on_shutdown_polling)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        logging.critical(f"BOT STOPPED {e}")
