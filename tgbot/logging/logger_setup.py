import logging
import betterlogging as bl
import asyncio

from aiogram import Bot


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


def setup_logging(bot: Bot, chat_id: int = None, log_level: int = logging.INFO):
    # цветной вывод в консоль
    bl.basic_colorized_config(level=log_level)
    logger = logging.getLogger('logger_setup')

    # Устанавливаем уровень логирования
    logger.setLevel(log_level)

    # Создаем хендлер для отправки логов в Telegram
    telegram_handler = TelegramLogHandler(bot=bot, chat_id=chat_id)
    telegram_handler.setLevel(log_level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    telegram_handler.setFormatter(formatter)

    logger.addHandler(telegram_handler)
    logger.info("Starting bot")

    # Возвращаем логгер для использования в других файлах
