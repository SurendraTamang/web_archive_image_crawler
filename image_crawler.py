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
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")

        # Assuming the navigation links can be found under a tag with class "navbar"
        # or an id "menu". Adjust the selector as needed.
        nav_elements = await page.query_selector_all('li > a')

        nav_urls = []
        for nav_element in nav_elements:
            href = await nav_element.get_attribute('href')
            nav_urls.append(href)

        for index, nav_url in enumerate(nav_urls):
            # Go to the linked page
            try:
                await page.goto(nav_url, wait_until="networkidle")

                # Create a subdirectory for this page
                nav_last_name = nav_url.split("/")[-1].split(".")[0]
                sub_dir_name = os.path.join(dir_name, f'{nav_last_name}')

                await download_all_images(page, sub_dir_name)
            except Exception as e:
                print(e)

        await browser.close()

if __name__ == "__main__":
    # Replace with the URL of your website
    url = 'https://web.archive.org/web/20200808135827/http://urgenmstypokhara.com/'
    # Replace with the path where you want to save the images
    dir_name = 'img'
    asyncio.run(scrape_images(url, dir_name))
