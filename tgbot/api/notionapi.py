
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
