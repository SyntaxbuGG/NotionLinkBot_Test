import asyncio
import logging

import betterlogging as bl
import orjson
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.handlers.commands import router
from tgbot.handlers.working_db import db_router
from tgbot.data import config


class TelegramLogHandler(logging.Handler):
    """Custom logging handler to send logs to a Telegram channel."""

    def __init__(self, bot: Bot, chat_id: int):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    async def send_log(self, record: logging.LogRecord):
        """Send a log message to the Telegram channel."""
        try:
            log_message = self.format(record)  # Форматирует запись в читаемый текст
            await self.bot.send_message(chat_id=self.chat_id, text=log_message)
        except Exception as e:
            print(f"Failed to send log to Telegram: {e}")

    def emit(self, record: logging.LogRecord):
        # Используем asyncio.create_task, чтобы отправка лога не блокировала выполнение кода
        asyncio.create_task(self.send_log(record))


def setup_logging(bot: Bot, chat_id: int = None):
    log_level = logging.INFO
    # цветной вывод в консоль
    bl.basic_colorized_config(level=log_level)
    logger = logging.getLogger(__name__)

    # Устанавливаем уровень логирования
    logger.setLevel(logging.INFO)

    # Создаем хендлер для отправки логов в Telegram
    telegram_handler = TelegramLogHandler(bot=bot, chat_id=chat_id)
    telegram_handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    telegram_handler.setFormatter(formatter)

    logger.addHandler(telegram_handler)
    logger.info("Starting bot")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.session.close()
    await dispatcher.storage.close()


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
        print("BOT STOPPED")
