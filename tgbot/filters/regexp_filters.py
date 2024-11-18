import re
import asyncio

get_tld =  re.compile(r'((https?://)?[а-яa-zA-Z0-9\-]+\.(\w{2,6})(?:/[^\s]*)?)', re.IGNORECASE)
get_links = re.compile(r'(https?://[а-яa-zA-Z0-9\-]+\.\w{2,6}(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.\w{2,6})', re.IGNORECASE)

async def get_link_from_text(text: str):

    ltd = get_links.findall(text)
      
    return ltd
# Используем asyncio для запуска асинхронной функции
async def main():
    result = await get_link_from_text("Посмотрите на этот сайт: instagram.com/abbos и на другой http://kinogo.ru kron.ru/settings")
    print(result)

# Запуск программы
asyncio.run(main())