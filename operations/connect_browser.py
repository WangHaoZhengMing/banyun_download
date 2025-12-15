from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import asyncio


async def connect_to_browser_and_page(target_url: str,target_title: str, port: int = 9222) -> tuple[Browser, Page]:
    """
    连接到现有的浏览器实例并找到指定URL的页面
    
    Args:
        target_url: 目标页面的URL
        target_title: 目标页面的标题
        port: 浏览器调试端口
        
    Returns:
        tuple[Browser, Page]: 浏览器实例和页面对象
        
    Raises:
        RuntimeError: 如果未找到指定URL的页面
    """
    print(f"连接到调试界面 (端口: {port})...")
    
    p = await async_playwright().start()
    
    # 连接到现有的浏览器实例
    # 使用 127.0.0.1 而不是 localhost，以避免 IPv6 (::1) 解析问题
    browser: Browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
    
    context: BrowserContext = browser.contexts[0]
    page: Page = None

    # 查找具有特定标题的页面
    if target_title:
        for p in context.pages:
            if target_title in await p.title():
                page = p
                print(f"已连接到现有页面: {await page.title()}")
                break
    # 如果通过标题没有找到页面，并且提供了URL，则按URL查找
    if not page and target_url:
        for p in context.pages:
            if target_url in p.url:
                page = p
                print(f"已连接到现有页面: {p.url}")
                break

    # 如果两种方式都找不到页面，则抛出错误
    if not page:
        print("未找到指定页面，将创建新页面...")
        page = await context.new_page()
        if target_url:
            await page.goto(target_url,wait_until="domcontentloaded",timeout=120000)
            print(f"已在新页面中打开URL: {target_url}")
        else:
            print("未提供目标URL，打开空白页面。")

    await page.bring_to_front()
    print(f"页面标题: {await page.title()}")
    
    # 等待页面稳定
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)
    
    # 获取页面基本信息
    title: str = await page.title()
    print(f"页面标题: {title}")
    print(f"当前URL: {page.url}")
    
    return browser, page
