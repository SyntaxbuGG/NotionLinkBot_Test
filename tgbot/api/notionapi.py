import httpx
import asyncio
from tgbot.data import config

print(config.DATABASE_ID_NOTION)


async def create_page(link, user_id, domain):
    headers = {
        "Authorization": f"Bearer {config.INTEGRATION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = {
        "parent": {"type": "database_id", "database_id": config.DATABASE_ID_NOTION},
        "properties": {
            "title": {"title": [{"text": {"content": "test"}}]},
            "id_user_tg": {"number": user_id},
            "category": {"rich_text": [{"text": {"content": "test"}}]},
            "url": {"url": link},
            "source": {"rich_text": [{"text": {"content": domain}}]},
        },
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/pages", headers=headers, json=data
        )

        # Проверка статуса ответа
        if response.status_code == 200:
            print("Page created successfully!")
            print(
                response.json()
            )  # Выводим ответ от API (например, ID созданной страницы)
        else:
            print(f"Error: {response.status_code}")
            print(response.json())


async def get_and_update_data_from_notion(user_id, link, category, title, priority):
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
                else:
                    print(
                        f"Error updating page {page_id}: {update_response.status_code}"
                    )

        else:
            print(f"Error fetching data: {response.status_code}")
            print(response.json())


# Запуск асинхронной функции
# asyncio.run(get_data_from_notion())
