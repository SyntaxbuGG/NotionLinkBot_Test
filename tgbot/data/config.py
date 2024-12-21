import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN")

DATABASE_URL: str = os.getenv("DATABASE_URL")

INTEGRATION_TOKEN: str = os.getenv("INTEGRATION_TOKEN")
DATABASE_ID_NOTION: str = os.getenv("DATABASE_ID_NOTION")


CHAT_ID:int = os.getenv('CHAT_ID')
