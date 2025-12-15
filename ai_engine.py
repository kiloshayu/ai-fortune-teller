from openai import OpenAI
import json
import os

def get_ai_analysis(api_key, bazi_text, birth_year):
    """
    OpenAI 兼容模式：一次性获取 0-100 岁全周期数据 + 综合评分
    """
    if not api_key:
        return {"error": "API Key 为空"}

    # ⚠️ 保持你之前的配置
    BASE_URL = "https://xh.v1api.cc/v1" 
    
    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
    except Exception as e:
        return {"error": f"客户端初始化失败: {str(e)}"}

    # 计算 100 岁时间跨度
    start_year = birth_year
    end_year = birth_year + 100

    prompt = f"""
    你是一个精通《三命通会》与华尔街量化分析的专家。
    请根据用户的八字，生成从 {start_year} 年（出生）到 {end_year} 年（100岁）的完整人生量化报告。

    【用户信息】
    {bazi_text}

    【任务要求】
    1. **全周期K线**：生成每年流年运势数据 (Open/High/Low/Close, 基准50分)。
       - 大运交脱年份或重大转折年，High/Low 波动要大。
    2. **五维雷达图**：请给该命局打分 (0-100分)：
       - 财富 (Wealth)
       - 事业 (Career)
       - 感情 (Love)
       - 健康 (Health)
       - 贵人 (Social)
    3. **全网排名**：预估该命格层次击败了全国多少人 (例如 95%)。
    4. **重大事件**：在 timeline 中，对于极为重要的年份，在 "event" 字段标记事件（如：结婚、生子、升职、大病、发财），普通年份留空。

    【输出格式】
    严格返回纯 JSON 对象（不要 Markdown），结构如下：
    {{
        "ranking": 92,
        "radar": {{
            "wealth": 85,
            "career": 90,
            "love": 70,
            "health": 60,
            "social": 88
        }},
        "timeline": [
            {{
                "year": {start_year},
                "ganzhi": "干支",
                "open": 50, "high": 50, "low": 50, "close": 50,
                "event": "出生",
                "comment": "批语..."
            }},
            ... (直到 {end_year} 年)
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
