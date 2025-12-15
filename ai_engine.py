from openai import OpenAI
import json
import os

def get_ai_analysis(api_key, bazi_text, birth_year):
    """
    OpenAI 兼容模式：引入【大运锚定权重算法】
    """
    if not api_key:
        return {"error": "API Key 为空"}

    BASE_URL = "https://xh.v1api.cc/v1" 
    
    try:
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
    except Exception as e:
        return {"error": f"客户端初始化失败: {str(e)}"}

    start_year = birth_year
    end_year = birth_year + 80

    # --- 核心提示词升级：加入权重逻辑 ---
    prompt = f"""
    你是一个精通《三命通会》与华尔街量化算法的专家。
    请根据用户的八字，采用【大运权重锚定法】生成从 {start_year} 到 {end_year} 年的量化数据。

    【用户信息】
    {bazi_text}

    【核心算法规则】 (必须严格遵守)
    1. **大运定趋势 (Trend)**: 
       - 大运决定了股价的“箱体”区间。
       - 喜用神大运：基准分设为 70-80 分（牛市）。
       - 忌神/刑冲大运：基准分设为 30-40 分（熊市）。
       - 平运：基准分 50 分。
    2. **流年定波动 (Volatility)**:
       - 流年是在“大运基准分”的基础上进行加减分（幅度 +/- 20分）。
       - **重要原则**：如果是“忌神大运”中的“喜用流年”，分数不能给太高（例如基准30 + 流年20 = 50分），这叫“熊市反弹”。
       - **重要原则**：如果是“喜用大运”中的“忌神流年”，分数不能给太低（例如基准80 - 15 = 65分），这叫“牛市回调”。
    3. **输出要求**:
       - 必须体现出明显的“十年一换运”的阶梯感。

    【输出数据结构】
    严格返回纯 JSON，结构如下：
    {{
        "ranking": 92,
        "radar": {{ "wealth": 80, "career": 80, "love": 60, "health": 70, "social": 85 }},
        "timeline": [
            {{
                "year": {start_year},
                "ganzhi": "干支",
                "dayun": "当前所属大运(如甲午)",
                "open": 45, 
                "high": 48, 
                "low": 40, 
                "close": 42, 
                "event": "",
                "comment": "大运为忌(基准40)，流年平平，低位震荡。"
            }},
            ...
        ]
    }}
    """

    try:
        model_name = "gemini-3-pro-preview" 

        response = client.chat.completions.create(
            model=model_name, 
            messages=[
                {"role": "system", "content": "You are a Quant Analyst. Output JSON only."},
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
