from regex import T
from tgbot.database.sqlalchemydb import NotionInterDb, TgLinkUsers
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

    async def save_data_url(self, data_url, user_id, category, user_link):
        try:
            with Session(self.engine) as session:
                for link, data_link in zip(user_link, data_url):
                    if not data_link:
                        data_link = {}

                    # через pipeline анализируем текст
                    get_priority = analyze_priority(data_link.get("text",False))
                    print(get_priority)

                    await get_and_update_data_from_notion(
                        user_id=user_id,
                        link=link,
                        category=category,
                        title=data_link.get("title",'Unknown'),
                        priority=get_priority,
                    )
                    stmt = select(TgLinkUsers).filter_by(id_user_tg=user_id, url=link)
                    get_result = session.scalar(stmt)
                    if get_result:
                        get_result.title = data_link.get("title",'Unknown')
                        get_result.category = category
                        get_result.priority = get_priority
                        session.add(get_result)
                    else: 
                        print('Не сохранился')
                        return False
                    session.commit()

        except Exception as e:
            print(e)
            return False



    async def save_notion_id_token(self,user_id,integration_token,database_id):
        try:
            with Session(self.engine) as session:
                stmt = select(NotionInterDb).filter_by(id_user_tg = user_id)
                print(integration_token)
                print(database_id)
        
                result = session.scalar(stmt)
                print(result)
                if not result:
                    new_record = NotionInterDb(
                    id_user_tg = user_id,
                    integration_token = integration_token,
                    database_id = database_id,
                    )
                    session.add(new_record)
                    session.commit()
                    return True    
                else:
                    return False
                
        except Exception as e:
            print(e)
            return e

                

    async def get_notion_id_token(self,user_id):
        try:
          
            with Session(self.engine) as sesion:
                stmt = select(NotionInterDb).filter_by(id_user_tg = user_id)
                query = sesion.scalar(stmt)
                print(query)
                if query:
                    
                    return query.database_id, query.integration_token
                else:
                    print('Пользователь не существует') 
                    return False                       
        except Exception as e:
            print(f'Ошибка подключение к базуданных {e}')
            return False