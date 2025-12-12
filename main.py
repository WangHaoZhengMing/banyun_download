import asyncio
import os
from operations.download_page import download_page
from operations.add_paper import save_new_paper
from operations.connect_browser import connect_to_browser_and_page
from playwright.async_api import Browser, Page
from urllib.parse import quote

async def check_paper_exists(page: Page, paper_title: str) -> bool:
    encoded_paper_name = quote(paper_title)
    check_url = f"https://tps-tiku-api.staff.xdf.cn/paper/check/paperName?paperName={encoded_paper_name}&operationType=1&paperId="
    try:
        # Use page's context to make the request, bypassing CORS issues.
        api_response = await page.context.request.get(check_url)
        data = await api_response.json()
        print(data)
        if data.get("data", {}).get("repeated"):
            log_file_path = os.path.join(os.path.dirname(__file__), '..', 'other', '重复.txt')
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(paper_title + '\n')
            return True
    except Exception as e:
        print(f"API request failed for '{paper_title}': {e}")
    return False

async def main():
    page_number = 33
    for i in range(page_number,466): 
        zujvanwang_catalogue_url=f"https://zujuan.xkw.com/czkx/shijuan/jdcs/p{i}"
        print(f"Processing page {i}...")
        browser, page = await connect_to_browser_and_page(port=2001, target_url=zujvanwang_catalogue_url, target_title="")
        zujvanwang_papers = await page.eval_on_selector_all(
            "div.info-item.exam-info a.exam-name",
            "elements => elements.map(el => ({url: 'https://zujuan.xkw.com' + el.getAttribute('href'), title: el.innerText.trim()}))"
        )
        for item in zujvanwang_papers:
            browser: Browser
            page: Page
            browser, page = await connect_to_browser_and_page(target_url=item["url"],port=2001,target_title="")
            page_data = await download_page(page)
            if not await check_paper_exists(page, page_data.name):
                await save_new_paper(page_data)
            
        await browser.close()
    await browser.close()



if __name__ == "__main__":
    asyncio.run(main())