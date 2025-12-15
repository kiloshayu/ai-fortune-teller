import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from bazi import get_bazi_text
from ai_engine import get_ai_analysis

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="AI 命理量化终端",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# --- 2. 黑金风格 CSS 注入 (极简、黑色底、高对比度) ---
st.markdown("""
<style>
    /* 全局背景黑 */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* 侧边栏背景深灰 */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    /* 输入框样式 */
    .stTextInput input, .stSelectbox, .stDateInput {
        color: #fff !important;
    }
    /* 去除顶部红条和Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 关键指标卡片样式 */
    .metric-card {
        background-color: #21262D;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #58A6FF; /* 科技蓝 */
    }
    .metric-label {
        font-size: 14px;
        color: #8B949E;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏逻辑 ---
with st.sidebar:
    st.markdown("### ⚙️ 量化参数设置")
    api_key = st.text_input("API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    st.markdown("### 👤 命主档案")
    birth_date = st.date_input("出生日期", value=datetime(1996, 2, 29))
    birth_time = st.time_input("出生时间", value=datetime.strptime("07:30", "%H:%M").time())
    gender = st.selectbox("性别", ["男", "女"])
    
    st.markdown("---")
    # 删除了“预测年份”滑块，改为固定逻辑
    st.info("📊 默认预测模式：出生 - 100岁")
    
    run_btn = st.button("⚡ 开始 AI 演算", type="primary", use_container_width=True)

# --- 4. 主界面逻辑 ---

# 标题区
st.markdown("## 📈 Life-Quant Alpha | 人生量化交易终端")
st.markdown(f"<div style='color: #8B949E; font-size: 0.9em; margin-bottom: 20px;'>命主代码: {birth_date.strftime('%Y%m%d')} | 策略模型: Gemini-Pro-Quant-V3</div>", unsafe_allow_html=True)

if run_btn and api_key:
    with st.spinner("🔄 正在从宇宙数据库拉取数据 (0-100岁全周期)..."):
        # 1. 八字排盘
        bazi_info = get_bazi_text(birth_date.year, birth_date.month, birth_date.day, birth_time.hour)
        
        # 2. AI 演算 (固定 100 年)
        raw_data = get_ai_analysis(api_key, bazi_info, birth_date.year)
        
        # 错误处理
        if "error" in raw_data:
            st.error(f"❌ 演算中断: {raw_data['error']}")
        else:
            # 数据提取
            timeline = raw_data.get("timeline", [])
            radar = raw_data.get("radar", {})
            ranking = raw_data.get("ranking", 50)
            
            df = pd.DataFrame(timeline)

            # --- 第一部分：核心指标仪表盘 (Top Metrics) ---
            col1, col2, col3, col4 = st.columns(4)
            
            def metric_html(label, value, suffix=""):
                return f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}{suffix}</div>
                </div>
                """
            
            with col1: st.markdown(metric_html("全网命格排位", f"{ranking}", "%"), unsafe_allow_html=True)
            with col2: st.markdown(metric_html("财富指数", radar.get('wealth', 0)), unsafe_allow_html=True)
            with col3: st.markdown(metric_html("事业指数", radar.get('career', 0)), unsafe_allow_html=True)
            with col4: st.markdown(metric_html("综合评分", int(df['close'].mean())), unsafe_allow_html=True)

            st.markdown("---")

            # --- 第二部分：图表区 (K线 + 雷达) ---
            chart_col1, chart_col2 = st.columns([3, 1])
            
            # 1. 绘制 K 线图 (左侧大图)
            with chart_col1:
                # 筛选出有事件的年份进行标注
                event_df = df[df['event'].notna() & (df['event'] != "")]
                
                fig_k = go.Figure(data=[go.Candlestick(
                    x=df['year'],
                    open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                    increasing_line_color='#26A69A', # 涨-绿
                    decreasing_line_color='#EF5350', # 跌-红
                    text=df['comment'],
                    name="运势K线"
                )])

                # 添加重大事件标注 (Annotations)
                annotations = []
                for index, row in event_df.iterrows():
                    annotations.append(dict(
                        x=row['year'],
                        y=row['high'],
                        xref="x", yref="y",
                        text=f"🚩{row['event']}",
                        showarrow=True,
                        arrowhead=1,
                        ax=0, ay=-30,
                        font=dict(color="#FFD700", size=10)
                    ))
                
                fig_k.update_layout(
                    title="Life Trend (0-100 Years)",
                    template="plotly_dark", # 核心：使用 Plotly 自带暗黑模板
                    paper_bgcolor='rgba(0,0,0,0)', # 透明背景融入网页
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=500,
                    xaxis_rangeslider_visible=False,
                    annotations=annotations,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_k, use_container_width=True)

            # 2. 绘制雷达图 (右侧小图)
            with chart_col2:
                categories = ['财富', '事业', '感情', '健康', '贵人']
                r_values = [radar.get('wealth',50), radar.get('career',50), radar.get('love',50), radar.get('health',50), radar.get('social',50)]
                
                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=r_values,
                    theta=categories,
                    fill='toself',
                    fillcolor='rgba(88, 166, 255, 0.3)',
                    line_color='#58A6FF'
                ))
                fig_r.update_layout(
                    title="命局五维图",
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100]),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_r, use_container_width=True)

            # --- 第三部分：详细事件流 ---
            st.markdown("### 🗓️ 关键人生节点 (Key Events)")
            
            # 只显示有重大事件的年份
            if not event_df.empty:
                for _, row in event_df.iterrows():
                    with st.expander(f"{row['year']}年 ({row['ganzhi']}) - {row['event']}"):
                        st.write(f"**AI 批语：** {row['comment']}")
                        st.progress(int(row['close']), text=f"当年能量指数: {row['close']}")
            else:
                st.info("平稳的一生，暂无极端波动事件。")

elif run_btn and not api_key:
    st.warning("⚠️ 请输入 API Key 启动系统")
