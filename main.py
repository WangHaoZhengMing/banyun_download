import asyncio
import os
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum
from operations.download_page import download_page
from operations.add_paper import save_new_paper
from operations.connect_browser import connect_to_browser_and_page
from playwright.async_api import Browser, Page
from urllib.parse import quote


# Type aliases 
type PaperUrl = str
type PaperTitle = str
type PaperId = str


class ProcessResult(Enum):
    """处理结果枚举"""
    SUCCESS = "success"
    ALREADY_EXISTS = "already_exists"
    FAILED = "failed"


@dataclass
class PaperInfo:
    """试卷信息"""
    url: PaperUrl
    title: PaperTitle


@dataclass
class ProcessError:
    """错误信息"""
    message: str
    exception: Optional[Exception] = None
    
    def __str__(self) -> str:
        if self.exception:
            return f"{self.message}: {self.exception}"
        return self.message


# Result type 
type Result[T] = Tuple[Optional[T], Optional[ProcessError]]


async def check_paper_exists(page: Page, paper_title: PaperTitle) -> Result[bool]:
    """检查试卷是否已存在
    
    Returns:
        Result[bool]: (存在状态, 错误信息)
    """
    encoded_paper_name: str = quote(paper_title)
    check_url: str = f"https://tps-tiku-api.staff.xdf.cn/paper/check/paperName?paperName={encoded_paper_name}&operationType=1&paperId="
    
    try:
        api_response = await page.context.request.get(check_url)
        data: Dict = await api_response.json()
        print(data)
        
        if data.get("data", {}).get("repeated"):
            log_file_path: str = os.path.join(os.path.dirname(__file__), 'other', '重复.txt')
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write(paper_title + '\n')
            return (True, None)
        
        return (False, None)
        
    except Exception as e:
        error: ProcessError = ProcessError(
            message=f"API request failed for '{paper_title}'",
            exception=e
        )
        print(f"❌ {error}")
        return (None, error)


async def fetch_paper_list(page: Page) -> Result[List[PaperInfo]]:
    """获取目录页的试卷列表
    
    Returns:
        Result[List[PaperInfo]]: (试卷列表, 错误信息)
    """
    try:
        papers_data: List[Dict[str, str]] = await page.eval_on_selector_all(
            "div.info-item.exam-info a.exam-name",
            "elements => elements.map(el => ({url: 'https://zujuan.xkw.com' + el.getAttribute('href'), title: el.innerText.trim()}))"
        )
        
        papers: List[PaperInfo] = [
            PaperInfo(url=item["url"], title=item["title"]) 
            for item in papers_data
        ]
        
        return (papers, None)
        
    except Exception as e:
        error: ProcessError = ProcessError(
            message="Failed to fetch paper list",
            exception=e
        )
        return (None, error)


async def process_single_paper(
    paper_info: PaperInfo,
    port: int,
    tiku_page: Page
) -> Result[ProcessResult]:
    """处理单个试卷
    
    Returns:
        Result[ProcessResult]: (处理结果, 错误信息)
    """
    paper_browser: Optional[Browser] = None
    paper_page: Optional[Page] = None
    
    try:
        # 连接到试卷页面
        paper_browser, paper_page = await connect_to_browser_and_page(
            target_url=paper_info.url,
            port=port,
            target_title=""
        )
        
        # 下载页面数据
        page_data = await download_page(paper_page)
        
        # 检查是否已存在
        exists_result, exists_error = await check_paper_exists(tiku_page, page_data.name)
        
        if exists_error is not None:
            return (None, exists_error)
        
        if exists_result:
            print(f"⚠️ 试卷已存在: {page_data.name}")
            return (ProcessResult.ALREADY_EXISTS, None)
        
        # 保存新试卷
        await save_new_paper(page_data, tiku_page)
        print(f"✅ 成功处理: {page_data.name}")
        return (ProcessResult.SUCCESS, None)
        
    except Exception as e:
        error: ProcessError = ProcessError(
            message=f"Failed to process paper: {paper_info.url}",
            exception=e
        )
        import traceback
        traceback.print_exc()
        return (None, error)
        
    finally:
        # 关闭页面和浏览器，防止内存泄漏
        if paper_page is not None:
            try:
                await paper_page.close()
            except Exception:
                pass
        if paper_browser is not None:
            try:
                await paper_browser.close()
            except Exception:
                pass


async def process_catalogue_page(
    page_number: int,
    port: int,
    tiku_page: Page
) -> Result[int]:
    """处理单个目录页
    
    Returns:
        Result[int]: (成功处理的试卷数, 错误信息)
    """
    catalogue_url: str = f"https://zujuan.xkw.com/czkx/shijuan/jdcs/p{page_number}"
    catalogue_browser: Optional[Browser] = None
    catalogue_page: Optional[Page] = None
    success_count: int = 0
    
    try:
        print(f"📖 Processing catalogue page {page_number}...")
        
        # 连接到目录页面
        catalogue_browser, catalogue_page = await connect_to_browser_and_page(
            port=port,
            target_url=catalogue_url,
            target_title=""
        )
        
        # 获取试卷列表
        papers_result, papers_error = await fetch_paper_list(catalogue_page)
        
        if papers_error is not None:
            return (None, papers_error)
        
        if papers_result is None:
            return (None, ProcessError(message="Failed to fetch paper list: result is None"))
            
        papers: List[PaperInfo] = papers_result
        print(f"📄 Found {len(papers)} papers on page {page_number}")
        
        # 处理每个试卷 (并发)
        print(f"⚡ Starting concurrent processing for {len(papers)} papers...")
        
        # 创建任务列表
        tasks = [
            process_single_paper(paper, port, tiku_page)
            for paper in papers
        ]
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks)
        
        # 统计结果
        for idx, (single_result, single_error) in enumerate(results):
            paper = papers[idx]
            if single_error is None and single_result == ProcessResult.SUCCESS:
                success_count += 1
            elif single_error is not None:
                print(f"❌ Error processing '{paper.title}': {single_error}")
        
        return (success_count, None)
        
    except Exception as e:
        error: ProcessError = ProcessError(
            message=f"Failed to process catalogue page {page_number}",
            exception=e
        )
        import traceback
        traceback.print_exc()
        return (None, error)
        
    finally:
        if catalogue_browser is not None:
            try:
                await catalogue_browser.close()
            except Exception:
                pass


async def main() -> int:
    """主函数
    
    Returns:
        int: 退出码 (0=成功, 1=失败)
    """
    # 确保必要的目录存在
    directories: List[str] = ['PDF', 'output_toml', 'other']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # 配置参数
    start_page: int = 58
    end_page: int = 466
    debug_port: int = 2001
    total_success: int = 0

    target_url = ""
    target_title = "题库平台 | 录排中心"
    browser: Browser
    tiku_page: Page
    browser, tiku_page = await connect_to_browser_and_page(target_url=target_url, target_title=target_title,port=2001)
    
    print(f"🚀 Starting paper download process...")
    print(f"📊 Page range: {start_page} - {end_page}")
    print(f"🔌 Browser port: {debug_port}")
    print("=" * 60)
    
    for page_num in range(start_page, end_page):
        result, error = await process_catalogue_page(page_num, debug_port, tiku_page)
        
        if error is None and result is not None:
            total_success += result
            print(f"✅ Page {page_num} completed: {result} papers processed")
        elif error is not None:
            print(f"❌ Page {page_num} failed: {error}")
        else:
            print(f"❌ Page {page_num} failed: Unknown error (result is None)")
        
        # 延迟避免请求过快
        await asyncio.sleep(1)
        print("=" * 60)
    
    print(f"\n🎉 Process completed! Total papers processed: {total_success}")
    return 0


if __name__ == "__main__":
    exit_code: int = asyncio.run(main())
    exit(exit_code)