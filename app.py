import os
import asyncio
from playwright.async_api import async_playwright
import aiohttp


async def download_image(session, url, pathname):
    async with session.get(url) as resp:
        with open(pathname, 'wb') as f:
            f.write(await resp.read())


async def download_all_images(page, dir_name):
    img_elements = await page.query_selector_all('img')

    # Create the directory to store images if it doesn't exist
    os.makedirs(dir_name, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for img_element in img_elements:
            src = await img_element.get_attribute('src')
            if src:
                filename = src.split("/")[-1]
                pathname = os.path.join(dir_name, filename)
                tasks.append(download_image(session, src, pathname))

        await asyncio.gather(*tasks)


async def scrape_images(url, dir_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await download_all_images(page, dir_name)
        await browser.close()


if __name__ == "__main__":
    # Replace with the URL of your website
    url = 'https://web.archive.org/web/20200808135827/http://urgenmstypokhara.com/'
    dir_name = 'ammodations'  # Replace with the path where you want to save the images
    asyncio.run(scrape_images(url, dir_name))
