import re

from playwright.async_api import async_playwright


async def parse_price_for_ozon(url, xpath):
    from technesis.config import logger

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",  # noqa E501
        )
        context.set_default_timeout(10000)

        page = await context.new_page()

        price = None
        try:
            # Переходим на указанную страницу
            await page.goto(url)
            for x in range(0, 200, 10):  # Перемещаем мышь постепенно
                await page.mouse.move(x, 100)
            # Ищем элемент по xpath
            element = page.locator(f"xpath={xpath}")
            price_str = await element.text_content()
            # Чистим строку от лишних символов
            price = int(re.sub(r"[^\d.,]", "", price_str).replace(",", "."))
        except Exception as e:
            logger.info(f"Error: {e}")

        await browser.close()

        return price
