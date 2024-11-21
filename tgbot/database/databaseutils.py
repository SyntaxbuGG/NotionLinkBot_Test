from tgbot.database.sqlalchemydb import TgLinkUsers
from tgbot.nlp_test.text_priority import analyze_priority
from tgbot.api.notionapi import get_and_update_data_from_notion

from sqlalchemy.orm import Session
from sqlalchemy import select
from urllib.parse import urlparse


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine

    def save_user_links(
        self,
        link: str,
        user_id: int,
        source_link: str,
        source_sender: str,
    ) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = select(TgLinkUsers).where(
                    TgLinkUsers.id_user_tg == user_id, TgLinkUsers.url == link
                )
                result = session.scalar(stmt)
                if result:
                    return True

                tg_user = TgLinkUsers(
                    id_user_tg=user_id,
                    url=link,
                    source_link=source_link,
                    source_sender=source_sender,
                )
                session.add(tg_user)

                session.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    def get_user_links(self, user_id):
        try:
            all_links = []
            with Session(self.engine) as session:
                stmt = select(TgLinkUsers).filter_by(id_user_tg=user_id)
                result = session.scalars(stmt)
                if result:
                    for link in result:
                        all_links.append(link.url)

                    return all_links
                else:
                    print("Пользователь в базе данных отсуствует")
                    return False
        except Exception as e:
            print(f"Ошибка извлечение данных {e}")
            return False

    async def save_data_url(self, data_url: list[list], user_id, category, user_link):
        try:
            with Session(self.engine) as session:
                for link, data_link in zip(user_link, data_url):
                    # через pipeline анализируем текст
                    get_priority = analyze_priority(data_link["text"])
                    await get_and_update_data_from_notion(
                        user_id=user_id,
                        link=link,
                        category=category,
                        title=data_link["title"],
                        priority=get_priority,
                    )
                    stmt = select(TgLinkUsers).filter_by(id_user_tg=user_id, url=link)
                    get_result = session.scalar(stmt)
                    if get_result:
                        get_result.title = data_link["title"]
                        get_result.category = category
                        get_result.priority = get_priority
                        session.add(get_result)
                    session.commit()

        except Exception as e:
            print(e)
