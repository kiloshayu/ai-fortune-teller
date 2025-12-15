import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from bazi import get_bazi_text
from ai_engine import get_ai_analysis

# --- 1. 页面基础配置 (必须是第一个Streamlit命令) ---
st.set_page_config(
    page_title="QUANT LIFE | 人生量化终端",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# --- 2. 高级黑金风格 CSS 注入 ---
# 我们不再暴力涂黑，而是使用渐变和卡片设计
st.markdown("""
<style>
    /* 1. 全局背景：深空灰蓝渐变，营造深邃感 */
    .stApp {
        background: linear-gradient(to bottom right, #0a0c10, #121826);
        color: #E0E0E0; /* 柔和的灰白文字，不刺眼 */
    }

    /* 2. 侧边栏：磨砂深色玻璃感 */
    [data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.95);
        border-right: 1px solid rgba(255, 215, 0, 0.1); /* 极细微的金色边框 */
    }

    /* 3. 输入控件美化 */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTimeInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    /* 聚焦时高亮金色 */
    .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 5px rgba(255, 215, 0, 0.3);
    }

    /* 4. 核心指标卡片 (玻璃拟态 + 黑金风格) */
    div.metric-card {
        background: linear-gradient(145deg, rgba(30, 35, 45, 0.8), rgba(20, 25, 35, 0.9));
        border: 1px solid rgba(255, 215, 0, 0.25); /* 金色边框 */
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); /* 深度阴影 */
        backdrop-filter: blur(4px);
        transition: transform 0.3s ease;
    }
    div.metric-card:hover {
        transform: translateY(-5px); /* 鼠标悬停轻微上浮 */
        border-color: rgba(255, 215, 0, 0.5);
    }
    .metric-label {
        font-size: 14px;
        color: #8B949E;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        /* 金色渐变文字 */
        background: linear-gradient(to right, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(255, 215, 0, 0.2);
    }

    /* 5. 按钮美化：金色主按钮 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #FFD700 0%, #FF8C00 100%);
        border: none;
        color: #000;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button[kind="primary"]:hover {
         box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
         transform: scale(1.02);
    }

    /* 6. 隐藏默认元素 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    [data-testid="stToolbar"] {visibility: hidden;} /* 隐藏图表右上角的工具栏 */
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏逻辑 (重构，隐藏 API 输入框) ---
with st.sidebar:
    st.markdown("## 🏛️ QUANT LIFE<br>核心参数设定", unsafe_allow_html=True)
    st.markdown("---")
    
    # 【优化】用折叠面板隐藏 API Key 输入框，显得更整洁
    with st.expander("🔑 API 通行证 (必填)", expanded=False):
        st.caption("请输入您的量化服务密钥以启动核心算法。")
        # 尝试从 secrets 读取，方便部署，本地则手动输入
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            st.success("✅ 已安全加载云端密钥")
        else:
            api_key = st.text_input("输入密钥 (sk-...)", type="password", key="api_input", label_visibility="collapsed")

    st.markdown("### 👤 命主主要档案")
    with st.container(): # 使用容器包裹，增加一点内边距
        birth_date = st.date_input("出生日期", value=datetime(1996, 2, 29), min_value=datetime(1900, 1, 1))
        birth_time = st.time_input("出生时间", value=datetime.strptime("07:30", "%H:%M").time())
        gender = st.selectbox("性别", ["男", "女"])
    
    st.markdown("---")
    st.info("📊 模型状态：已加载 (Gemini-Pro-Quant-V3)\n\n📅 预测周期：出生 - 100周岁")
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("⚡ 启动量化演算引擎", type="primary", use_container_width=True)

# --- 4. 主界面逻辑 ---

# 标题区：模仿金融终端的抬头
st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0;'>📈 QUANT LIFE ALPHA</h1>", unsafe_allow_html=True)
st.markdown(f"""
<div style='color: #8B949E; font-size: 0.9em; margin-bottom: 30px; font-family: monospace;'>
    > 终端状态: 在线 | 命主代码: {birth_date.strftime('%Y%m%d')}-{gender} | 数据源: 宇宙能量场(模拟)
</div>
""", unsafe_allow_html=True)

if run_btn:
    if not api_key:
        st.error("⚠️ 演算中断：未检测到有效的 API 通行证。请在侧边栏输入。")
    else:
        # 使用进度条增加仪式感
        progress_bar = st.progress(0, text="🚀 初始化连接...")
        try:
            progress_bar.progress(20, text="🌌 正在进行八字排盘与能量定一定...")
            # 1. 八字排盘
            bazi_info = get_bazi_text(birth_date.year, birth_date.month, birth_date.day, birth_time.hour)
            
            progress_bar.progress(50, text="🧠 接入 AI 量化模型，正在推演百年流年 (耗时较长，请耐心等待)...")
            # 2. AI 演算 (固定 100 年)
            raw_data = get_ai_analysis(api_key, bazi_info, birth_date.year)
            
            progress_bar.progress(90, text="📊 正在生成可视化图表报告...")

            # 错误处理
            if "error" in raw_data:
                st.error(f"❌ 演算失败: {raw_data['error']}")
            else:
                # 数据提取
                timeline = raw_data.get("timeline", [])
                radar = raw_data.get("radar", {})
                ranking = raw_data.get("ranking", 50)
                df = pd.DataFrame(timeline)
                progress_bar.empty() # 清除进度条

                # --- 第一部分：黑金风格核心指标卡片 ---
                col1, col2, col3, col4 = st.columns(4)
                
                # 使用注入的CSS类名来构建HTML卡片
                def metric_html(label, value, suffix=""):
                    return f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value">{value}<span style="font-size:16px; color:#FFD700;">{suffix}</span></div>
                    </div>
                    """
                
                with col1: st.markdown(metric_html("全网命格排位", f"{ranking}", "%"), unsafe_allow_html=True)
                with col2: st.markdown(metric_html("财富能量指数", radar.get('wealth', 0)), unsafe_allow_html=True)
                with col3: st.markdown(metric_html("事业成就指数", radar.get('career', 0)), unsafe_allow_html=True)
                with col4: 
                    avg_score = int(df['close'].mean()) if not df.empty else 0
                    st.markdown(metric_html("人生综合均分", avg_score), unsafe_allow_html=True)

                st.markdown("---")

                # --- 第二部分：图表区 ---
                chart_col1, chart_col2 = st.columns([3, 1])
                
                # 1. 绘制 K 线图 (左侧大图)
                with chart_col1:
                    st.markdown("#### 📉 百年人生走势 K 线 (Life Trend)")
                    # 筛选出有事件的年份进行标注
                    event_df = df[df['event'].notna() & (df['event'] != "")]
                    
                    fig_k = go.Figure(data=[go.Candlestick(
                        x=df['year'],
                        open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                        increasing_line_color='#00E676', # 涨-荧光绿
                        decreasing_line_color='#FF3D00', # 跌-荧光红
                        text=df['comment'],
                        hoverinfo='x+y+text',
                        name="运势K线"
                    )])

                    # 添加重大事件标注
                    annotations = []
                    for index, row in event_df.iterrows():
                        annotations.append(dict(
                            x=row['year'], y=row['high'] + 2,
                            xref="x", yref="y",
                            text=f"🚩{row['event']}",
                            showarrow=False,
                            font=dict(color="#FFD700", size=11),
                            bgcolor="rgba(0,0,0,0.5)",
                            borderpad=4
                        ))
                    
                    fig_k.update_layout(
                        template="plotly_dark", # 使用深色模板
                        paper_bgcolor='rgba(0,0,0,0)', # 透明背景
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=550,
                        xaxis_rangeslider_visible=False,
                        annotations=annotations,
                        margin=dict(l=10, r=10, t=30, b=10),
                        xaxis=dict(showgrid=False, color='#8B949E'),
                        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', color='#8B949E')
                    )
                    st.plotly_chart(fig_k, use_container_width=True, config={'displayModeBar': False})

                # 2. 绘制雷达图 (右侧小图)
                with chart_col2:
                    st.markdown("#### 🎯 命局五维雷达")
                    categories = ['财富 (Wealth)', '事业 (Career)', '感情 (Love)', '健康 (Health)', '贵人 (Social)']
                    r_values = [radar.get('wealth',50), radar.get('career',50), radar.get('love',50), radar.get('health',50), radar.get('social',50)]
                    r_values.append(r_values[0]) # 闭合雷达图
                    categories.append(categories[0])

                    fig_r = go.Figure()
                    fig_r.add_trace(go.Scatterpolar(
                        r=r_values,
                        theta=categories,
                        fill='toself',
                        fillcolor='rgba(255, 215, 0, 0.2)', # 金色填充
                        line_color='#FFD700', # 金色线条
                        marker=dict(color='#FFD700', size=6)
                    ))
                    fig_r.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#8B949E')),
                            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#FFD700')),
                            bgcolor='rgba(0,0,0,0)'
                        ),
                        height=450,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_r, use_container_width=True, config={'displayModeBar': False})

                # --- 第三部分：详细事件流 (时间轴样式) ---
                st.markdown("---")
                st.markdown("### 🗓️ 关键人生节点复盘 (Key Events Review)")
                
                if not event_df.empty:
                    for _, row in event_df.iterrows():
                        # 使用带边框的容器替代 expander，更像时间轴节点
                        with st.container():
                            st.markdown(f"""
                            <div style="border-left: 3px solid #FFD700; padding-left: 15px; margin-bottom: 20px;">
                                <h4 style="color: #FFD700; margin: 0;">{row['year']}年 ({row['ganzhi']}) | <span style="color: #fff;">{row['event']}</span></h4>
                                <p style="color: #B0B8C3; font-style: italic; margin: 5px 0;">“{row['comment']}”</p>
                                <div style="font-size: 0.8em; color: #8B949E;">当年能量指数: <span style="color: #FFD700;">{row['close']}</span> (基准50)</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("注：AI 判定该命局一生较为平稳，暂无极端显著的转折事件。")

        except Exception as e:
             st.error(f"系统内部错误: {e}")
             progress_bar.empty()

else:
    # 初始状态显示一个占位提示
    st.markdown("""
    <div style='text-align: center; color: #505a6b; padding: 50px;'>
        Start the engine from the sidebar to generate alpha.
        <br>⬅️ 请在侧边栏输入参数并启动演算引擎。
    </div>
    """, unsafe_allow_html=True)
