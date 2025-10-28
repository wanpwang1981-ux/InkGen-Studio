import asyncio
from playwright.async_api import async_playwright, expect
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 1. Navigate to the local HTML file
        # We use os.path.abspath to ensure the path is correct
        file_path = os.path.abspath('frontend/index.html')
        await page.goto(f'file://{file_path}')

        # 2. Initialize a project
        await page.get_by_label("小說標題:").fill("星際之夢")
        await page.get_by_label("大綱檔案路徑:").fill("docs/flowchart.md") # Using a dummy file for testing
        await page.get_by_role("button", name="初始化專案").click()

        # Wait for the success message to appear in the log
        await expect(page.locator("#log-container p:has-text('Project \\'星際之夢\\' initialized successfully.')")).to_be_visible(timeout=5000)

        # 3. Start novel generation
        await page.get_by_role("button", name="開始生成").click()

        # Wait for the task status polling to kick in
        await expect(page.locator("#log-container p:has-text('Task started successfully!')")).to_be_visible(timeout=5000)
        await expect(page.locator("#log-container p:has-text('System will now periodically check the task status.')")).to_be_visible(timeout=5000)

        # Wait a bit for the first poll to happen
        await asyncio.sleep(3.5)
        await expect(page.locator("#log-container p:has-text('is currently: pending')")).to_be_visible(timeout=5000)


        # 4. Take a screenshot
        screenshot_path = 'jules-scratch/verification/verification.png'
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        await browser.close()

if __name__ == '__main__':
    # Since we are using async playwright, we need to run it in an event loop
    asyncio.run(main())