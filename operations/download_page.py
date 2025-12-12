import re
from bs4 import BeautifulSoup
from playwright.async_api import Page as PlaywrightPage

from operations.model import question_page
from operations.model import questionData
import json
from pathlib import Path
import tomli_w



async def download_page(playwright_page: PlaywrightPage) -> question_page:
     # Extract all styles and sec-list elements HTML
    elements_data = await playwright_page.evaluate("""
        () => {
            // Get all stylesheets
            const styles = Array.from(document.styleSheets)
                .map(sheet => {
                    try {
                        return Array.from(sheet.cssRules)
                            .map(rule => rule.cssText)
                            .join('\\n');
                    } catch (e) {
                        return '';
                    }
                })
                .join('\\n');
            
            // Get all sec-list elements
            const sections = Array.from(document.querySelectorAll('.sec-list'));
            return {
                styles: styles,
                elements: sections.map(el => el.outerHTML)
            };
        }
    """)
    
    print(f"Found {len(elements_data['elements'])} question sections.")

    questions = []
    # format stems into plain text and put them into stemlist
    for element_html in elements_data['elements']:
        soup = BeautifulSoup(element_html, 'html.parser')
        exam_item_cnt = soup.find('div', class_='exam-item__cnt')
        origin_element = soup.select_one('a.ques-src')
        
        stem = exam_item_cnt.get_text(strip=True) if exam_item_cnt else "Stem not found"
        origin = origin_element.get_text(strip=True) if origin_element else "Origin not found"
        
        if exam_item_cnt:
            questions.append(questionData(origin=origin, stem=stem))

    title = await playwright_page.evaluate("""
        () => {
            const titleElement = document.querySelector('.title-txt .txt');
            return titleElement ? titleElement.innerText : 'Title not found';
        }
    """)
    title = re.sub(r'[/\\:*?"<>|]', '', title)

    # exract info
    info = await playwright_page.evaluate("""
        () => {
            const items = document.querySelectorAll('.info-list .item');
            if (items.length >= 2) {
                return {
                    shengfen: items[0].innerText.trim(),
                    nianji: items[1].innerText.trim()
                };
            }
            return { shengfen: 'Not found', nianji: 'Not found' };
        }
    """)

    # Extract subject
    subject_text = await playwright_page.evaluate("""
        () => {
            const subjectElement = document.querySelector('.subject-menu__title .title-txt');
            return subjectElement ? subjectElement.innerText.trim() : 'Subject not found';
        }
    """)

    valid_subjects = ['语文', '数学', '英语', '物理', '化学', '生物', '历史', '政治', '地理', '科学']
    subject = 'Unknown'
    for s in valid_subjects:
        if s in subject_text:
            subject = s
            break

    year_matches = re.findall(r'\d{4}', title)
    year = 2024  # 默认年份
    for year_str in year_matches:
        year_int = int(year_str)
        if 2001 <= year_int <= 2030:
            year = year_int
            break

    page_data = question_page(
        name=title,
        province=info['shengfen'],
        grade=info['nianji'],
        year=year,
        subject=subject,
        stemlist=questions
    )
    # in there save the All.sec-list to pdf named title.pdf
    await playwright_page.pdf(path=f"./PDF/{title}.pdf")
    print(f"Saved PDF: ./PDF/{title}.pdf")

    # await playwright_page.close()
    # Convert page_data to JSON and save to output directory
    # output_dir = Path("./output_toml")
    # output_dir.mkdir(parents=True, exist_ok=True)
    # toml_path = output_dir / f"{title}.toml"
    # page_data_dict = {
    #     'name': page_data.name,
    #     'province': page_data.province,
    #     'grade': page_data.grade,
    #     'year': page_data.year,
    #     'subject': page_data.subject,
    #     'page_id': page_data.page_id if page_data.page_id else None,
    #     'stemlist': [{'origin': q.origin, 'stem': q.stem} for q in page_data.stemlist]
    # }
    # with open(toml_path, 'wb') as f:
    #     tomli_w.dump(page_data_dict, f)
    # print(f"Saved TOML: {toml_path}")


    return page_data

