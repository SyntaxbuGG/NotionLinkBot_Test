import asyncio
import aiohttp
from bs4 import BeautifulSoup






async def fetch_data(session,url):
    # Ensure the URL includes the scheme (http:// or https://)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    async with session.get(url) as response:
        data_url = {}
        html = await response.text()
        soup = BeautifulSoup(html,'html.parser')

        title = soup.title.string.strip() if soup.title else "No title"

        # meta_description = soup.find("meta", attrs={"name": "description"})
        # description = meta_description["content"] if meta_description else "No description found"

        paragraphs = soup.find_all('p')
        text = " ".join(p.get_text() for p in paragraphs[:5])
        # извлечь категорию через мета-теги
        # meta_category = soup.find("meta", attrs={"name": "category"})
        # category = meta_category["content"] if meta_category else "Category not found"  


      
        data_url = {"title":title, "text": text}
        return data_url



async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results
    



# print(asyncio.run(main(urls)))