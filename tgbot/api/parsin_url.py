import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger("logger_setup")


async def fetch_data(session, url):
    # Ensure the URL includes the scheme (http:// or https://)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        async with session.get(url) as response:
            data_url = {}
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            title = soup.title.string.strip() if soup.title else "No title"

            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs[:5])

            data_url = {"title": title, "text": text}
            return data_url
    except aiohttp.ClientConnectorError as e:
        logger.warning(f"""error": f"Connection failed for {url}: {str(e)}""")
        return False
    except Exception as e:
        logger.warning(f"""error": f"An error occurred for {url}: {str(e)}""")
        return False


async def main(urls: list):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


