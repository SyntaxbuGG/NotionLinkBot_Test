import asyncio
import logging
import httpx

from urllib.parse import urlparse

from tgbot.nlp_test.text_priority import analyze_priority
from tgbot.data import config


logger = logging.getLogger("logger_setup")


async def create_page(link, user_id, source_sender, category, title, priority):
    # Попался на circular import, надо отложенный импорт
    from tgbot.handlers.working_db import db_manager

    get_priority = await analyze_priority(priority)
    source_link = urlparse(link).netloc or "Unknown"

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
            "category": {"rich_text": [{"text": {"content": category}}]},
            "title": {"title": [{"text": {"content": title}}]},
            "priority": {"rich_text": [{"text": {"content": get_priority}}]},
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/pages", headers=headers, json=data
        )

        # Проверка статуса ответа
        if response.status_code == 200:
            logger.debug("Page created successfully!")
            return True

        elif response.status_code == 400:
            logger.error("Bad request - invalid data.")
            print(response.json())
            return False
        
        # Ограничение количества запросов: Notion имеет лимит на количество запросов в секунду (RPS)
        elif response.status_code == 409:  # Обработка ошибки 409
            logger.error(f"Conflict error: {response.status_code}")
            await asyncio.sleep(1)  # Пауза перед повторным запросом
            return await create_page(link, user_id, source_sender, category, title, priority) 

        else:
            logger.critical(f"Error: {response.status_code}")
            print(response.json())
            return False


# В дальнейшем если надо взять из Notion database
# async def get_and_update_data_from_notion(user_id, link, category, title, priority):
#     # Попался на circular import надо отложенный импорт
#     from tgbot.handlers.working_db import db_manager

#     check_user_exist = await db_manager.get_notion_id_token(user_id=user_id)
#     if check_user_exist:
#         config.INTEGRATION_TOKEN = check_user_exist[1]
#         config.DATABASE_ID_NOTION = check_user_exist[0]
#     headers = {
#         "Authorization": f"Bearer {config.INTEGRATION_TOKEN}",
#         "Notion-Version": "2022-06-28",
#     }

#     # Фильтрация по нескольким полям одновременно (например, по user_id и url)
#     query = {
#         "filter": {
#             "and": [
#                 {
#                     "property": "id_user_tg",  # Первое условие: id_user_tg
#                     "number": {
#                         "equals": user_id  # Пример: ID пользователя
#                     },
#                 },
#                 {
#                     "property": "url",  # Второе условие: link
#                     "url": {
#                         "equals": link  # Пример: ссылка
#                     },
#                 },
#             ]
#         }
#     }

#     async with httpx.AsyncClient() as client:
#         # Запрос на фильтрацию данных
#         response = await client.post(
#             f"https://api.notion.com/v1/databases/{config.DATABASE_ID_NOTION}/query",
#             headers=headers,
#             json=query,
#         )

#         if response.status_code == 200:
#             data = response.json()
#             logger.debug(f"Data retrieved successfully! {data}")

#             # Получаем все найденные записи
#             results = data.get("results", [])

#             # Обновляем найденные записи0
#             for page in results:
#                 page_id = page["id"]  # ID страницы для обновления
#                 update_data = {
#                     "properties": {
#                         "category": {"rich_text": [{"text": {"content": category}}]},
#                         "title": {"title": [{"text": {"content": title}}]},
#                         "priority": {"rich_text": [{"text": {"content": priority}}]},
#                     }
#                 }

#                 # Отправляем запрос для обновления записи
#                 update_response = await client.patch(
#                     f"https://api.notion.com/v1/pages/{page_id}",
#                     headers=headers,
#                     json=update_data,
#                 )
#                 data_json_update = update_response.json()

#                 if update_response.status_code == 200:
#                     logger.debug(f"Page {page_id} updated successfully!")
#                     return True

#                 elif update_response.status_code == 400:
#                     logger.warning(f"Bad request - {data_json_update}")
#                     return False
#                 else:
#                     logger.error(f"Error updating page {page_id}: {data_json_update}")
#                     return False

#         else:
#             logger.critical(f"Error fetching data: {response.json()}")
#             return False


async def check_notion_credentials(id_token_notion):
    headers = {
        "Authorization": f"Bearer {id_token_notion['integration_token']}",
        "Notion-Version": "2022-06-28",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.notion.com/v1/databases/{id_token_notion['database_id']}",
                headers=headers,
            )
            print(response.status_code)
            if response.status_code == 200:
                return 1
            elif response.status_code == 401:
                logger.warning("Invalid integration token.")
                return -1
            elif response.status_code == 404:
                logger.warning("Database ID not found.")
                return -2
            else:
                logger.error(f"Unexpected error: {response.status_code}")
                return False

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_detail = e.response.json() if e.response.text else "No additional details"

        if status_code == 401:
            logger.warning("Authentication error: Check your integration token.")
            return -1
        elif status_code == 404:
            logger.warning("Not found: Check your DATABASE_ID.")
            return -2
        else:
            logger.warning(f"HTTP error occurred: {status_code} - {error_detail}")
            return False

    except httpx.ReadTimeout:
        logger.warning("The request timed out. Please try again later.")
        return False

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False


async def pages_create_async(links, user_id, source_sender, category, data_urls):
    """Асинхронное сохранение нескольких ссылок в базе данных Notion"""
    tasks = [
        create_page(
            link=link,
            user_id=user_id,
            source_sender=source_sender,
            category=category,
            priority=data.get("text", False),
            title=data.get("title", "unknown"),
        )
        for link, data in zip(links, data_urls)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
