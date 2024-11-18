import httpx
import asyncio


integration_token = "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"

database_id = "141996c06b93808c8e28fc92fb0a1a3f"
headers = {
    "Authorization": f"Bearer {integration_token}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

data = {
    "parent": {"type": "database_id", "database_id": database_id},
    "properties": {
        "title" : {
            "title" : [{"text": {"content": "test"}}]
        },
        "category":{
         
            "rich_text":  [{"text": {"content": "zbkogdabudet"}}]
        }


    }

}
async def create_page():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/pages", headers=headers, json=data
        )
        
        # Проверка статуса ответа
        if response.status_code == 200:
            print("Page created successfully!")
            print(response.json())  # Выводим ответ от API (например, ID созданной страницы)
        else:
            print(f"Error: {response.status_code}")
            print(response.json())

# Запуск асинхронной функции
asyncio.run(create_page())