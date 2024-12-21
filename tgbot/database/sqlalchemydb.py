from datetime import datetime
import asyncio

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from sqlalchemy.types import BigInteger, DateTime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncAttrs

from tgbot.data import config as cfg


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TgLinkUsers(Base):
    __tablename__ = "tg_link"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_user_tg: Mapped[int] = mapped_column(BigInteger)
    url: Mapped[str] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=True)
    category: Mapped[str] = mapped_column(nullable=True)
    priority: Mapped[str] = mapped_column(nullable=True)
    source_link: Mapped[str] = mapped_column(nullable=True)
    source_sender: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"User_table_id : {self.id},\nUser_tg_id: {self.id_user_tg}\nUsername_tg: {self.tg_username}\nDict_users: {self.dict_users}"


class NotionInterDb(Base):
    __tablename__ = "notion_id_token"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_user_tg: Mapped[int] = mapped_column(BigInteger)
    database_id: Mapped[str] = mapped_column(nullable=True)
    integration_token: Mapped[str] = mapped_column(nullable=True)


engine = create_async_engine(cfg.DATABASE_URL, echo=True)


# Использование run_sync для асинхронной работы
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(create_tables())
