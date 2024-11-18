import re
import asyncio


text2 = """salom kalesan : instagram.com/abbos/salom i na drugoy mir http://kinogo.ru kron.ru/
                                      settings как ты братан еще есть почта zarbotbekovabbosbek@gmai.com 
                                      https://curvy-sombrero-f8e.notion.site/12efe546b0fe80b2ac50e4229904cb22"""

# Регулярное выражение для поиска ссылок, включая путь и параметры
hard_search_links = re.compile(
    r"(https?://[a-zA-Z0-9\-]+\.[a-zA-Z]*(?:.[a-zA-Z]*)?(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.\w{2,15}(?:/[^\s]*)?)",
    re.IGNORECASE,
)

hard_search_links2 = re.compile(
    r"(https?://[a-zA-Z0-9\-]+\.[a-zA-Z]{2,15}(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.[a-zA-Z]{2,15}(?:/[^\s]*)?)",
    re.IGNORECASE,
)


async def get_links_from_text(text: str):
    # Ищем все ссылки в тексте
    links = hard_search_links.findall(text)
    return links

async def main():
    text = "Ознакомиться с ними необходимо перед вторым тестовым заданием. Сайт: https://curvy-sombrero-f8e.notion.site/12efe546b0fe80b2ac50e4229904cb22/salom/ebat g и ещё один http://example.com/abc"
    result = await get_links_from_text(text2)
    print(result)

# Запуск программы
asyncio.run(main())
