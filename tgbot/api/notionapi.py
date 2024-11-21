import httpx
import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tgbot.data import config


async def create_page(link, user_id, source_link, source_sender):
    # Попался на circular import, надо отложенный импорт
    from tgbot.handlers.working_db import db_manager

    check_user_exist = await db_manager.get_notion_id_token(user_id=user_id)
    if check_user_exist:
        config.INTEGRATION_TOKEN = check_user_exist[1]
        config.DATABASE_ID_NOTION = check_user_exist[0]

    headers = {
        "Authorization": f"Bearer {config.INTEGRATION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = {
        "parent": {"type": "database_id", "database_id": config.DATABASE_ID_NOTION},
        "properties": {
            "id_user_tg": {"number": user_id},
            "url": {"url": link},
            "source_link": {"rich_text": [{"text": {"content": source_link}}]},
            "source_sender": {"rich_text": [{"text": {"content": source_sender}}]},
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/pages", headers=headers, json=data
        )

        # Проверка статуса ответа
        if response.status_code == 200:
            print("Page created successfully!")
            print(response.json())

        elif response.status_code == 400:
            return False

        else:
            print(f"Error: {response.status_code}")
            print(response.json())
            return False


async def get_and_update_data_from_notion(user_id, link, category, title, priority):
    # Попался на circular importю надо отложенный импорт
    from tgbot.handlers.working_db import db_manager

    check_user_exist =await db_manager.get_notion_id_token(user_id=user_id)
    if check_user_exist:
        config.INTEGRATION_TOKEN = check_user_exist[1]
        config.DATABASE_ID_NOTION = check_user_exist[0]
    headers = {
        "Authorization": f"Bearer {config.INTEGRATION_TOKEN}",
        "Notion-Version": "2022-06-28",
    }

    # Фильтрация по нескольким полям одновременно (например, по user_id и url)
    query = {
        "filter": {
            "and": [
                {
                    "property": "id_user_tg",  # Первое условие: id_user_tg
                    "number": {
                        "equals": user_id  # Пример: ID пользователя
                    },
                },
                {
                    "property": "url",  # Второе условие: link
                    "url": {
                        "equals": link  # Пример: ссылка
                    },
                },
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        # Запрос на фильтрацию данных
        response = await client.post(
            f"https://api.notion.com/v1/databases/{config.DATABASE_ID_NOTION}/query",
            headers=headers,
            json=query,
        )

        if response.status_code == 200:
            data = response.json()
            print("Data retrieved successfully!")
            print(data)

            # Получаем все найденные записи
            results = data.get("results", [])

            # Обновляем найденные записи
            for page in results:
                page_id = page["id"]  # ID страницы для обновления
                update_data = {
                    "properties": {
                        "category": {"rich_text": [{"text": {"content": category}}]},
                        "title": {"title": [{"text": {"content": title}}]},
                        "priority": {"rich_text": [{"text": {"content": priority}}]},
                    }
                }

                # Отправляем запрос для обновления записи
                update_response = await client.patch(
                    f"https://api.notion.com/v1/pages/{page_id}",
                    headers=headers,
                    json=update_data,
                )

                if update_response.status_code == 200:
                    print(f"Page {page_id} updated successfully!")

                elif update_response.status_code == 400:
                    return await False
                else:
                    print(
                        f"Error updating page {page_id}: {update_response.status_code}"
                    )
                    return await False

        else:
            print(f"Error fetching data: {response.status_code}")
            print(response.json())
            return await False


# Запуск асинхронной функции
# asyncio.run(get_data_from_notion())
