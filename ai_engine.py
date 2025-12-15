from openai import OpenAI
import json
import os

def get_ai_analysis(api_key, bazi_text, birth_year):
    """
    OpenAI 兼容模式：一次性获取 0-80 岁全周期数据 + 综合评分
    """
    if not api_key:
        return {"error": "API Key 为空"}

    # ⚠️ 保持你的中转配置
    BASE_URL = "https://xh.v1api.cc/v1" 
    
    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
    except Exception as e:
        return {"error": f"客户端初始化失败: {str(e)}"}

    # 设定预测范围 (0-80岁，太长AI容易超时)
    start_year = birth_year
    end_year = birth_year + 80

    prompt = f"""
    你是一个精通《三命通会》与华尔街量化分析的专家。
    请根据用户的八字，生成从 {start_year} 年（出生）到 {end_year} 年（80岁）的完整人生量化报告。

    【用户信息】
    {bazi_text}

    【任务要求】
    1. **全周期K线**：生成每年流年运势数据 (Open/High/Low/Close, 基准50分)。
       - 遇到“大运交脱”或“流年冲克”时，波动率(High-Low)要变大。
    2. **五维雷达图**：打分 (0-100分)：财富、事业、感情、健康、贵人。
    3. **全网排名**：预估命格击败了全国多少人 (%).
    4. **重大事件**：在 "event" 字段标记关键人生节点（如：考学、结婚、生子、发财、灾病），普通年份留空。

    【输出格式】
    严格返回纯 JSON 对象，结构如下：
    {{
        "ranking": 92,
        "radar": {{
            "wealth": 85, "career": 90, "love": 70, "health": 60, "social": 88
        }},
        "timeline": [
            {{
                "year": {start_year},
                "ganzhi": "干支",
                "open": 50, "high": 50, "low": 50, "close": 50,
                "event": "出生",
                "comment": "批语..."
            }},
            ...
        ]
    }}
    """

    try:
        # 使用你指定的模型
        model_name = "gemini-3-pro-preview" 

        response = client.chat.completions.create(
            model=model_name, 
            messages=[
                {"role": "system", "content": "You are a JSON data generator. Output raw JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            extra_body={"response_format": {"type": "json_object"}}
        )

        content = response.choices[0].message.content
        clean_json = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(clean_json)

    except Exception as e:
        return {"error": str(e)}
