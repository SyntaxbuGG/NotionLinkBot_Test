import logging
import asyncio

from urllib.parse import urlparse

from tgbot.database.sqlalchemydb import NotionInterDb, TgLinkUsers
from tgbot.nlp_test.text_priority import analyze_priority


from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select

logger = logging.getLogger("logger_setup")


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine
        self.AsyncSessionMaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def save_user_links(
        self,
        link: str,
        user_id: int,
        source_sender: str,
        priority: str,
        title: str,
        category: str
    ) -> bool:
        try:
            source_link = urlparse(link).netloc or "Unknown"
            get_priority = await analyze_priority(priority)
            async with self.AsyncSessionMaker() as session:
                stmt = select(TgLinkUsers).filter_by(id_user_tg=user_id, url=link)
                result = await session.execute(stmt)
                row = result.scalar()
                if not row:
                    tg_user = TgLinkUsers(
                        id_user_tg=user_id,
                        url=link,
                        source_link=source_link,
                        source_sender=source_sender,
                        priority=get_priority,
                        title=title,
                        category=category
                    )
                    session.add(tg_user)
                    await session.commit()
                return True
        except Exception as e:
            logger.critical(f"Ошибка при сохранении данных: {e}")
            return False

    async def get_user_links(self, user_id):
        try:
            all_links = []
            async with self.AsyncSessionMaker() as session:
                stmt = select(TgLinkUsers).filter_by(id_user_tg=user_id)
                result = await session.execute(stmt)
                row = result.scalars()
                if row:
                    for link in row:
                        all_links.append(link.url)

                    return all_links
                else:
                    logger.warning("Пользователь в базе данных отсуствует")
                    return False
        except Exception as e:
            logger.critical(f"Ошибка извлечение данных {e}")
            return False

    async def save_notion_id_token(self, user_id, integration_token, database_id):
        try:
            async with self.AsyncSessionMaker() as session:
                stmt = select(NotionInterDb).filter_by(id_user_tg=user_id)
                result = await session.execute(stmt)
                row = result.scalar()
                if not row:
                    new_record = NotionInterDb(
                        id_user_tg=user_id,
                        integration_token=integration_token,
                        database_id=database_id,
                    )
                    session.add(new_record)
                    await session.commit()
                    logger.info("New users added table NotionInterDb")
                    return True
                else:
                    return False

        except Exception as e:
            logger.warning(f"Error :{e}")

    async def get_notion_id_token(self, user_id):
        try:
            async with self.AsyncSessionMaker() as session:
                stmt = select(NotionInterDb).filter_by(id_user_tg=user_id)
                result = await session.execute(stmt)
                row = result.scalar()
                if row:
                    return (row.database_id, row.integration_token)
                else:
                    return False
        except Exception as e:
            logger.critical(f"Ошибка подключение к базу данных {e}")
            return False

    async def save_multiple_links(
        self,
        links: list[str],
        user_id: int,
        user_get_source: str,
        category: str,
        data_urls: dict,
    ) -> list[bool]:
        """Асинхронное сохранение нескольких ссылок в базе данных"""

        tasks = [
            self.save_user_links(
                link=link,
                user_id=user_id,
                source_sender=user_get_source,
                category=category,
                priority=data.get("text", False),
                title=data.get("title", "Unknown"),
            )
            for link, data in zip(links, data_urls)
        ]
        # Выполнение задач параллельно
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
