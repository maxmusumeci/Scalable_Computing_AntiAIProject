import asyncio
from playwright.async_api import async_playwright

URL = "http://127.0.0.1:5500/index.html"


async def get_slider_data(page):
    return await page.evaluate("""() => {
        return {
            targets: sliderState.targets.map(t => ({x: t.x, y: t.y})),
            order: sliderState.sliderOrder.map(c => c.name.toLowerCase()),
            sliders: sliderState.sliders.map(s => s.dataset.colorName)
        };
    }""")


async def drag_slider(page, slider_id, target_x):
    slider = await page.query_selector(slider_id)
    box = await slider.bounding_box()

    start_x = box["x"] + box["width"] / 2
    start_y = box["y"] + box["height"] / 2

    left_offset = target_x
    end_x = box["x"] + left_offset + box["width"]/2
    end_y = start_y

    steps = 30

    await page.dispatch_event(slider_id, 'pointerdown', {"button": 0, "clientX": start_x, "clientY": start_y})

    for i in range(steps):
        cur_x = start_x + (end_x - start_x) * (i + 1) / steps
        await page.mouse.move(cur_x, end_y)
        await asyncio.sleep(0.01)

    await page.dispatch_event(slider_id, 'pointerup', {"button": 0, "clientX": end_x, "clientY": end_y})


async def run_attacker():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        page = await browser.new_page()

        print("Opening page:", URL)
        await page.goto(URL)

        await page.wait_for_selector("#verifyBtn")
        await page.click("#verifyBtn")
        await page.wait_for_timeout(800)

        if "mode=slider" not in page.url:
            print("Not slider CAPTCHA, exiting.")
            return

        print("Slider CAPTCHA detected. Waiting for sliderState targets...")

        await page.wait_for_function("""() => sliderState && sliderState.targets && sliderState.targets.length === 3""")
        print("sliderState.targets ready!")

        data = await get_slider_data(page)
        targets = data["targets"]
        correct_order = data["order"]
        slider_colors = data["sliders"]

        print("Target positions:", targets)
        print("Expected order:", correct_order)
        print("Slider colors:", slider_colors)

        for color in correct_order:
            index = slider_colors.index(color)
            slider_id = f"#slider{index + 1}"
            tx = targets[index]["x"]

            print(f"Dragging {slider_id} to {tx}px")
            await drag_slider(page, slider_id, tx)
            await page.wait_for_timeout(300)

        print("Slider verification completed automatically!")
        await page.wait_for_timeout(2000)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(run_attacker())


