import asyncio
import requests
import sys
import os

# Ensure we can import from operations
sys.path.append(os.getcwd())

from operations.connect_browser import connect_to_browser_and_page
from operations.add_paper import get_upload_credentials, AUTH_HEADERS

async def test_get_credentials():
    print("🚀 开始测试获取凭证 (get_upload_credentials)...")
    
    # 1. 获取浏览器Cookies (模拟真实环境)
    print("1️⃣  正在连接浏览器获取Cookies...")
    target_title = "题库平台 | 录排中心"
    try:
        browser, page = await connect_to_browser_and_page(target_url="", target_title=target_title, port=2001)
    except Exception as e:
        print(f"❌ 连接浏览器失败: {e}")
        print("请确保浏览器已打开并登录目标网站，且开启了远程调试端口 2001")
        return

    cookies = await page.context.cookies()
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    print(f"✅ 获取到 {len(cookies_dict)} 个Cookies")
    
    await browser.close()

    # 2. 准备Session
    print("2️⃣  准备请求Session...")
    session = requests.Session()
    session.headers.update(AUTH_HEADERS)
    
    # 使用浏览器Cookies覆盖Header中的Cookies
    if "cookie" in session.headers:
        del session.headers["cookie"]
    session.cookies.update(cookies_dict)

    # 3. 调用测试函数
    test_filename = "test_credential_check.pdf"
    print(f"3️⃣  调用 get_upload_credentials, 文件名: {test_filename}")
    
    # 注意：get_upload_credentials 现在是 async 的，并且需要 page 对象
    # 我们需要重新连接浏览器并保持 page 打开
    print("🔄 重新连接浏览器以进行测试...")
    try:
        browser, page = await connect_to_browser_and_page(target_url="", target_title=target_title, port=2001)
    except Exception as e:
        print(f"❌ 连接浏览器失败: {e}")
        return

    result = await get_upload_credentials(page, test_filename)
    
    await browser.close()
    
    # 4. 验证结果
    if result:
        print("\n🎉 测试通过! 成功获取到凭证。")
        print("凭证数据概览:")
        for key, value in result.items():
            print(f"  - {key}: {str(value)[:50]}..." if isinstance(value, str) else f"  - {key}: {value}")
    else:
        print("\n❌ 测试失败: 未能获取凭证。")

if __name__ == "__main__":
    asyncio.run(test_get_credentials())
