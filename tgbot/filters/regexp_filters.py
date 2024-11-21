import re
import asyncio

get_tld =  re.compile(r'((https?://)?[а-яa-zA-Z0-9\-]+\.(\w{2,6})(?:/[^\s]*)?)', re.IGNORECASE)
get_links = re.compile(r'(https?://[а-яa-zA-Z0-9\-]+\.\w{2,6}(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.\w{2,6})', re.IGNORECASE)

async def get_link_from_text(text: str):

    ltd = get_links.findall(text)
      
    return ltd
# Используем asyncio для запуска асинхронной функции



async def get_id_token_notion(text: str):
    get_id = re.compile('INTEGRATION TOKEN:\s*(\w+)(?:.*)\s*DATABASE ID:\s+(\w+)')

    result = get_id.findall(text)

    return result




async def main():
    result = await get_link_from_text("https://docs.aiogram.dev/en/stable/utils/keyboard.html#aiogram.utils.keyboard.InlineKeyboardBuilder.adjust")
    print(result)




# Запуск программы
a= asyncio.run(get_id_token_notion("""@NotionLink_bot 
INTEGRATION TOKEN:4334332a22 21 5455454
DATABASE ID: salom3233suka 45544"""))
print(a)