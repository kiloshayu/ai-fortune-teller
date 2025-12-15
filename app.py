import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from bazi import get_bazi_text
from ai_engine import get_ai_analysis
import base64

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="QUANT LIFE | 人生量化终端",
    layout="wide",
    page_icon="🏛️",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 样式注入 (黑金风格 + 弹窗优化) ---
st.markdown("""
<style>
    /* 全局深色背景 */
    .stApp {
        background: linear-gradient(to bottom right, #0a0c10, #121826);
        color: #E0E0E0;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.95);
        border-right: 1px solid rgba(255, 215, 0, 0.1);
    }
    
    /* 输入框美化 */
    .stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    
    /* 确认框区域样式 */
    .confirmation-box {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-left: 5px solid #FFD700;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    /* 按钮样式 */
    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #FFD700 0%, #FF8C00 100%);
        border: none;
        color: #000;
        font-weight: bold;
    }
    
    /* 隐藏顶部红条 */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化 Session State (状态管理核心) ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'input' # 初始状态: input -> confirm -> result
if 'bazi_cache' not in st.session_state:
    st.session_state.bazi_cache = "" # 缓存排盘结果

# --- 4. 侧边栏：输入与控制 ---
with st.sidebar:
    st.markdown("## 🏛️ QUANT LIFE")
    st.markdown("---")
    
    with st.expander("🔑 API 通行证", expanded=False):
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            st.success("✅ 云端密钥已加载")
        else:
            api_key = st.text_input("输入密钥", type="password")

    st.markdown("### 👤 命主档案")
    birth_date = st.date_input("出生日期", value=datetime(1996, 2, 29), min_value=datetime(1900, 1, 1))
    birth_time = st.time_input("出生时间", value=datetime.strptime("07:30", "%H:%M").time())
    gender = st.selectbox("性别", ["男", "女"])
    
    st.markdown("---")
    
    # 【逻辑变更】按钮改为“排盘预览”
    if st.button("🔍 第一步：排盘预览", type="primary", use_container_width=True):
        st.session_state.stage = 'confirm'
        # 立即调用本地排盘代码
        st.session_state.bazi_cache = get_bazi_text(birth_date.year, birth_date.month, birth_date.day, birth_time.hour)
    
    if st.button("🔄 重置系统"):
        st.session_state.stage = 'input'
        st.rerun()

# --- 5. 主界面逻辑状态机 ---

st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0;'>📈 QUANT LIFE ALPHA</h1>", unsafe_allow_html=True)

# === 状态一：确认排盘信息 (Pop-up Window Simulation) ===
if st.session_state.stage == 'confirm':
    st.markdown("### 🛠️ 第二步：确认排盘信息")
    st.info("AI 有时会算错排盘。为确保量化准确，请检查下方信息。如果不准确，您可以直接在文本框中修改。")
    
    with st.container():
        # 这里允许用户修改排盘结果！
        edited_bazi = st.text_area(
            "八字与大运信息 (可编辑修正)", 
            value=st.session_state.bazi_cache, 
            height=250,
            help="如果大运时间不对，请直接在这里手动修改，AI 会以你修改后的为准。"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ 确认无误，开始演算", type="primary"):
                st.session_state.bazi_cache = edited_bazi # 更新为用户修改后的
                st.session_state.stage = 'result' # 进入结果页
                st.rerun() # 强制刷新页面
        with col2:
            st.caption("点击确认后，将消耗 Token 进行 AI 深度量化推演。")

# === 状态二：展示 AI 结果 (The Main Chart) ===
elif st.session_state.stage == 'result':
    if not api_key:
        st.error("⚠️ 缺少 API Key，无法演算。")
    else:
        with st.spinner("🚀 正在接入宇宙能量场，进行全周期量化 (约 20-30 秒)..."):
            # 调用 AI，传入的是用户确认过的 bazi_text
            raw_data = get_ai_analysis(api_key, st.session_state.bazi_cache, birth_date.year)
            
            if "error" in raw_data:
                st.error(f"❌ 演算失败: {raw_data['error']}")
                if st.button("返回修改"):
                    st.session_state.stage = 'confirm'
                    st.rerun()
            else:
                # --- 渲染图表 ---
                timeline = raw_data.get("timeline", [])
                radar = raw_data.get("radar", {})
                ranking = raw_data.get("ranking", 50)
                df = pd.DataFrame(timeline)

                # 1. 顶部指标
                col1, col2, col3, col4 = st.columns(4)
                # ... (此处省略简单的 HTML 指标代码，保持之前的样式即可，为节省篇幅) ...
                with col1: st.metric("全网排位", f"{ranking}%")
                with col2: st.metric("财富指数", radar.get('wealth', 0))
                with col3: st.metric("事业指数", radar.get('career', 0))
                with col4: st.metric("综合均分", int(df['close'].mean()) if not df.empty else 0)

                st.markdown("---")

                # 2. 交互式 K 线图 (核心升级点)
                # 筛选事件点
                event_df = df[df['event'].notna() & (df['event'] != "")]

                fig_k = go.Figure(data=[go.Candlestick(
                    x=df['year'],
                    open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                    increasing_line_color='#00E676', # 涨-绿
                    decreasing_line_color='#FF3D00', # 跌-红
                    name="运势",
                    # 增强 Tooltip 可读性
                    text=[f"<b>{row['year']} {row['ganzhi']}</b><br>{row['comment']}" for _, row in df.iterrows()],
                    hoverinfo='text+y'
                )])

                # 添加事件标注
                annotations = []
                for _, row in event_df.iterrows():
                    annotations.append(dict(
                        x=row['year'], y=row['high'],
                        xref="x", yref="y",
                        text=f"🚩{row['event']}",
                        showarrow=True,
                        arrowhead=1,
                        ax=0, ay=-40,
                        font=dict(color="#FFD700", size=12, family="Arial Black")
                    ))

                # 【核心升级】配置交互布局
                fig_k.update_layout(
                    title="人生量化走势图 (支持滚轮缩放/拖拽)",
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=600,
                    annotations=annotations,
                    
                    # === 交互核心配置 ===
                    xaxis=dict(
                        rangeslider=dict(visible=True), # 底部显示缩放滑块
                        type="linear",
                        gridcolor='rgba(255,255,255,0.1)',
                        fixedrange=False # 允许X轴缩放
                    ),
                    yaxis=dict(
                        gridcolor='rgba(255,255,255,0.1)',
                        fixedrange=False, # 允许Y轴缩放
                        title="能量指数"
                    ),
                    dragmode='pan', # 默认鼠标操作是平移
                    hovermode='x unified' # 统一显示X轴信息
                )
                
                st.plotly_chart(fig_k, use_container_width=True)
                
                # 3. 雷达图
                # ... (保持之前的雷达图代码) ...
                
                # 4. 详细事件流
                st.markdown("### 🗓️ 关键节点详情")
                if not event_df.empty:
                    st.dataframe(
                        event_df[['year', 'ganzhi', 'event', 'comment', 'close']],
                        column_config={
                            "year": "年份",
                            "ganzhi": "干支",
                            "event": "重大事件",
                            "comment": "AI 批语",
                            "close": st.column_config.ProgressColumn("能量分", min_value=0, max_value=100)
                        },
                        use_container_width=True,
                        hide_index=True
                    )

# === 状态零：默认欢迎页 ===
else:
    st.info("👈 请在左侧侧边栏输入信息，并点击“排盘预览”开始。")
