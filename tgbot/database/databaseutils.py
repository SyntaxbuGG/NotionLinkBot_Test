from sqlalchemy.orm import Session
from sqlalchemy import select
from tgbot.database.sqlalchemydb import TgLinkUsers


class DatabaseManager:
    def __init__(self, engine):
        self.engine = engine

    def save_user_links(self, selected_links: dict, query) -> bool:
        try:
            with Session(self.engine) as session:
                for value, link in selected_links.items():
                    stmt = select(TgLinkUsers).where(
                        TgLinkUsers.id_user_tg == query.from_user.id
                    )
                    tg_user = TgLinkUsers(
                        id_user_tg=query.from_user.id,
                        url=link,
                    )
                    session.add(tg_user)

                session.commit()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
            return False
