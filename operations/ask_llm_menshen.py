import openai
import json
import os


def text_from_file(file_path):
    """Read and return text content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""


async def ask_llm_for_analysis(page_data):
    print(f"Starting LLM check for: {page_data.name}")
    """
    Asks an LLM to check for potential errors in question data.

    Args:
        page_data: An object containing the name of the page data.
    """
    client = openai.AsyncOpenAI(
        base_url="http://menshen.xdf.cn/v1",
        api_key="26e96c4d312e48feacbd78b7c42bd71e",
    )

    input_file_path = os.path.join('operations', '..', 'other', 'detail', f'{page_data.name}_full.json')
    output_file_path = os.path.join('operations', '..', 'other', 'LLM_output', f'{page_data.name}_llm_check.json')

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            question_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file_path}")
        return

    prompt = f"""
    I want you to act as an expert in proofreading exam questions. I will provide you with a JSON file containing question data. In this data, 'origin' represents the source of the question as I have recorded it, and 'origin_from_our_bank' represents the source of the same question found in our system's question bank.

    Your task is to carefully compare the 'origin' with the sources listed in 'origin_from_our_bank'. A potential error exists if the 'origin_from_our_bank' does not contain a source that is the same as or very similar to the 'origin'. For example, if the origin is '2025·上海闵行·三模', the bank should contain something like '2025年上海市莘光学校中考三模英语试题'. If it doesn't, this could indicate that an old question has been mistakenly labeled as a new one.

    Please analyze the provided data and return ONLY a JSON object. This object must have a single key, "potential_errors", which contains a list of all the questions you've identified with potential errors.

    For each potential error, provide the following details:
    - "origin": The original source I recorded.
    - "stem": The question text.
    - "origin_from_our_bank": The list of sources from our system's bank.
    - "reason_for_error": A clear and concise explanation of why you believe there is an error.

    Here is an example of the exact output format I expect:
    {{
        "potential_errors": {{
            "stemlist": [
                {{
                    "origin": "2025·上海闵行·三模",
                    "stem": "10. Mike offered ______ Mary to carry her suitcase, but Mary said she could manage it herself.A．to helpB．helpC．helpingD．helped",
                    "origin_from_our_bank": [
                        ["人教新目标版八年级下学期 第三单元测试英语试题"],
                        ["人教新目标版英语八年级下册Unit 3 Could you please clean your room？Self Check 课时练习卷", "云南省楚雄彝族自治州2023-2024学年八年级下学期期中英语试题（含听力）"],
                        ["福建平潭一中教研片2024-2025学年九年级上学期英语期中适应性练习"],
                        ["2018年江苏省徐州市四县二区中考一模英语试题"]
                    ],
                    "reason_for_error": "您标记的来源是 '2025·上海闵行·三模'，但系统题库数据 'origin_from_our_bank' 中并未包含 '2025年上海市莘光学校中考三模英语试题'。这表明该题可能是一道旧题，被错误地标记为了新题。"
                }},
                {{
                    "origin": "2025·上海闵行·三模",
                    "stem": "25. Jim forgot to bring his dictionary, so Alice lent him______. (she)",
                    "origin_from_our_bank": [
                        ["2022年上海市青浦区中考二模英语试题（含听力）"],
                        ["2015届辽宁大石桥市水源二中中考模拟英语试卷"],
                        ["【万唯原创】2015年安徽省面对面英语（人教新目标Go For It）八年级(下)限时练"]
                    ],
                    "reason_for_error": "您标记的来源是 '2025·上海闵行·三模'，但系统题库数据 'origin_from_our_bank' 中并未包含 '2025年上海市莘光学校中考三模英语试题'。这表明该题可能是一道旧题，被错误地标记为了新题。"
                }}
            ]
        }}
    }}

    Now, please analyze the following question data:
    {json.dumps(question_data, ensure_ascii=False, indent=4)}
    """

    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="doubao-seed-1.6",
        )

        llm_response_str = chat_completion.choices[0].message.content
        
        # Clean the response string to ensure it's valid JSON
        # Remove markdown code block fences and strip whitespace
        if '```json' in llm_response_str:
            llm_response_str = llm_response_str.split('```json')[1].split('```')[0]
        
        llm_response_str = llm_response_str.strip()

        try:
            # The response is a string containing JSON, so we need to parse it.
            llm_response_json = json.loads(llm_response_str)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from LLM response. Error: {e}")
            print(f"LLM response was: {llm_response_str}")
            return

        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(llm_response_json, f, ensure_ascii=False, indent=4)
        
        print(f"Successfully saved LLM check to {output_file_path}")

    except Exception as e:
        print(f"An error occurred while communicating with the LLM or saving the file: {e}")


async def ask_llm_for_playload(message:str)->str:
    client = openai.AsyncOpenAI(
        base_url="http://menshen.xdf.cn/v1",
        api_key="26e96c4d312e48feacbd78b7c42bd71e",
    )
    sys_message = text_from_file("operations\\province_city.txt")
    response = await client.chat.completions.create(
        messages=[
            {   
                "role": "system",
                "content": sys_message,
            },
            {   
                "role": "user",
                "content": message,
            }
        ],
        model="doubao-seed-1.6",
    )
    print(response.choices[0].message.content)
    return response.choices[0].message.content
    


if __name__ == '__main__':
    import asyncio
    # from .model import question_page, provinces
    
    test_message:str = '2025年上海市莘光学校中考三模英语试题'

    message = f"请从试卷名称中提取出城市名称，只需要返回城市名称，格式为'城市'，如果没有包含省份和城市信息，请返回''。试卷名称：{test_message}.if it is not in the list,return未知. do not return extra info or string. you just need to return the city name!!!!!!!!!!!!!!"
    
    # Run the async function
    asyncio.run(ask_llm_for_city(message))
    




