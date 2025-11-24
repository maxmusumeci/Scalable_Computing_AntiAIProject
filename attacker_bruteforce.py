import asyncio
import random
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:5500/index.html"


async def drag_slider(page, slider_id, target_x):
    slider = await page.query_selector(slider_id)
    box = await slider.bounding_box()

    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2

    end_x = box["x"] + target_x + box["width"] / 2
    end_y = start_y

    await page.mouse.move(start_x, start_y)
    await page.mouse.down()
    await page.mouse.move(end_x, end_y, steps=30)
    await page.mouse.up()


async def run_attacker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        page = await browser.new_page()

        print("Opening homepage:", URL)
        await page.goto(URL)

        await page.wait_for_selector("#verifyBtn")
        await page.click("#verifyBtn")

        await page.wait_for_timeout(800)

        if "mode=slider" not in page.url:
            print("Not slider CAPTCHA, exiting program.")
            await browser.close()
            return

        print("Slider CAPTCHA detected, waiting for sliderState...")

        await page.wait_for_function("""
            () => sliderState
                  && sliderState.targets
                  && sliderState.targets.length === 3
        """)

        print("sliderState is ready! Performing continuous random slider movements...")

        try:
            while True:
                random_slider = random.randint(1, 3)
                slider_id = f"#slider{random_slider}"
                random_target_x = random.randint(30, 380)
                print(f"Randomly dragging {slider_id} to X offset {random_target_x}px")
                await drag_slider(page, slider_id, random_target_x)
                await page.wait_for_timeout(random.randint(500, 800))

        except KeyboardInterrupt:
            print("Stopping random slider movements...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_attacker())







