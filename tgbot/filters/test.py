import re
import asyncio

text1 = """📚 Темы и ресурсы для изучения/повторения (база) (https://curvy-sombrero-f8e.notion.site/12efe546b0fe80b2ac50e4229904cb22)

Ознакомиться с ними необходимо перед вторым тестовым заданием.

Даже если вы ранее работали с некоторыми из этих инструментов, рекомендуем освежить знания, чтобы уверенно выполнить второе задание."""


text2 = """salom kalesan : instagram.com/abbos/salom i na drugoy mir http://kinogo.ru kron.ru/
                                      settings как ты братан еще есть почта zarbotbekovabbosbek@gmai.com 
                                      https://curvy-sombrero-f8e.notion.site/12efe546b0fe80b2ac50e4229904cb22"""

# все ссылки будет захватывать кроме выше 6 знаков tld
get_links = re.compile(
    r"(https?://[а-яa-zA-Z0-9\-]+\.\w{2,15}(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.\w{2,15}(?:/[^\s]*)?)",
    re.IGNORECASE,
)

hard_search_links = re.compile(
    r"(https?://[а-яa-zA-Z0-9\-]+\.\w{2,15}(?:/[^\s]*)?|[а-яa-zA-Z0-9\-]+\.\w{2,15}(?:/[^\s]*)*)",
    re.IGNORECASE,
)

async def get_link_from_text(text: str):
    tld = get_links.findall(text)

    return tld


# Используем asyncio для запуска асинхронной функции
async def main():
    result = await get_link_from_text(text2)
    print(result)


# Запуск программы
asyncio.run(main())
