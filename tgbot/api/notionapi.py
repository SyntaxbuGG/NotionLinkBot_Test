import logging
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
            logging.debug("Page created successfully!")
            return True

        elif response.status_code == 400:
            logging.warning("Bad request - invalid data.")
            return False

        else:
            logging.error(f"Error: {response.status_code}")
            return False


async def get_and_update_data_from_notion(user_id, link, category, title, priority):
    # Попался на circular import надо отложенный импорт
    from tgbot.handlers.working_db import db_manager

    check_user_exist = await db_manager.get_notion_id_token(user_id=user_id)
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
            logging.debug(f"Data retrieved successfully! {data}")

            # Получаем все найденные записи
            results = data.get("results", [])

            # Обновляем найденные записи0
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
                data_json_update = update_response.json()

                if update_response.status_code == 200:
                    logging.debug(f"Page {page_id} updated successfully!")
                    return True

                elif update_response.status_code == 400:
                    logging.warning(f"Bad request - {data_json_update}")
                    return False
                else:
                    logging.error(f"Error updating page {page_id}: {data_json_update}")
                    return False

        else:
            logging.critical(f"Error fetching data: {response.json()}")
            return False


async def check_notion_credentials(user_id, id_token_notion):
    headers = {
        "Authorization": f"Bearer {id_token_notion['integration_token']}",
        "Notion-Version": "2022-06-28",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"https://api.notion.com/v1/databases/{id_token_notion['database_id']}",
                headers=headers,
            )
            print(response.status_code)
            if response.status_code == 200:
                return 1
            elif response.status_code == 401:
                logging.warning("Invalid integration token.")
                return -1
            elif response.status_code == 404:
                logging.warning("Database ID not found.")
                return -2
            else:
                logging.error(f"Unexpected error: {response.status_code}")
                return False

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_detail = e.response.json() if e.response.text else "No additional details"

        if status_code == 401:
            logging.warning("Authentication error: Check your integration token.")
            return -1
        elif status_code == 404:
            logging.warning("Not found: Check your DATABASE_ID.")
            return -2
        else:
            logging.warning(f"HTTP error occurred: {status_code} - {error_detail}")
            return False

    except httpx.ReadTimeout:
        logging.warning("The request timed out. Please try again later.")
        return False

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return False
