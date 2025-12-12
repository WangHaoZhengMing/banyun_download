from typing import Optional

from operations.connect_browser import connect_to_browser_and_page
from enum import IntEnum

class questionData:
    origin: str
    stem: str
    origin_from_our_bank: list[str]
    
    def __init__(self, origin: str, stem: str, origin_from_our_bank: Optional[list[str]] = None):
        self.origin = origin
        self.stem = stem
        self.origin_from_our_bank = origin_from_our_bank if origin_from_our_bank is not None else []

class question_page:
    name: str
    province: str
    grade: str
    year: int
    subject: str
    page_id: Optional[str] = None
    stemlist: list[questionData]

    def __init__(self, name: str, province: str, grade: str, year: int, subject: str, stemlist: list[questionData], page_id: Optional[str] = None):
        self.name = name
        self.province = province
        self.grade = grade
        self.year = year
        self.subject = subject
        self.stemlist = stemlist
class muti_thread_config:
    ports: list[int]
    zujvanwang_catalogue_url: str
    zujvanwang_papers: list[dict[str, str]]

    def __init__(self, ports: list[int], zujvanwang_catalogue_url: str, zujvanwang_papers: Optional[list[dict[str, str]]] = None):
        self.ports = ports
        self.zujvanwang_catalogue_url = zujvanwang_catalogue_url
        self.zujvanwang_papers = zujvanwang_papers if zujvanwang_papers is not None else []

    @classmethod
    async def create(cls, ports: list[int], zujvanwang_catalogue_url: str):
        browser, page = await connect_to_browser_and_page(port=2001, target_url=zujvanwang_catalogue_url, target_title="")
        zujvanwang_papers = await page.eval_on_selector_all(
            "div.info-item.exam-info a.exam-name",
            "elements => elements.map(el => ({url: 'https://zujuan.xkw.com' + el.getAttribute('href'), title: el.innerText.trim()}))"
        )
        if not zujvanwang_papers:
            print("Warning: Could not find any question URLs on the catalogue page.")
        print("close tabpage")
        # await page.close()
        return cls(ports, zujvanwang_catalogue_url, zujvanwang_papers)
    