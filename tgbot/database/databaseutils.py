from turtle import st
from tgbot.database.sqlalchemydb import TgLinkUsers

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
        domain: str,
    ) -> bool:
        try:
            with Session(self.engine) as session:
                stmt = (
                    select(TgLinkUsers)
                    .where(TgLinkUsers.id_user_tg)
                    .where(TgLinkUsers.url)
                )
                result = session.scalar(stmt)
                if result:
                    return True

                tg_user = TgLinkUsers(id_user_tg=user_id, url=link, source=domain)
                session.add(tg_user)

                session.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False

    def get_user_links(self,user_id):
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
            print(f'Ошибка извлечение данных {e}')
            return False