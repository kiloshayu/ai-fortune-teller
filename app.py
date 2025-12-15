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

# --- 2. CSS 样式 ---
st.markdown("""
<style>
    .stApp {background: linear-gradient(to bottom right, #0a0c10, #121826); color: #E0E0E0;}
    [data-testid="stSidebar"] {background-color: rgba(22, 27, 34, 0.95); border-right: 1px solid rgba(255, 215, 0, 0.1);}
    .stTextInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #fff !important;
        border-radius: 8px !important;
    }
    .confirmation-box {
        border: 1px solid #FFD700;
        background-color: rgba(255, 215, 0, 0.05);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化 Session State ---
if 'stage' not in st.session_state:
    st.session_state.stage = 'input'
if 'bazi_cache' not in st.session_state:
    st.session_state.bazi_cache = ""

# --- 4. 侧边栏 ---
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
    
    st.markdown("---")
    
    if st.button("🔍 第一步：排盘并核对", type="primary", use_container_width=True):
        st.session_state.stage = 'confirm'
        # 调用新的 bazi.py 生成详细的大运信息
        st.session_state.bazi_cache = get_bazi_text(birth_date.year, birth_date.month, birth_date.day, birth_time.hour, gender)
    
    if st.button("🔄 重置系统"):
        st.session_state.stage = 'input'
        st.rerun()

# --- 5. 主界面逻辑 ---

st.markdown("<h1 style='font-size: 2.5rem; margin-bottom: 0;'>📈 QUANT LIFE ALPHA</h1>", unsafe_allow_html=True)

# === 状态一：确认大运 (Confirmation Stage) ===
if st.session_state.stage == 'confirm':
    st.markdown("### 🛠️ 第二步：核对八字与大运")
    
    # 提示框
    st.markdown("""
    <div class="confirmation-box">
        <b>💡 系统提示：</b> 下方是根据算法排出的【大运表】。
        <br>请仔细核对 <b>起运年份</b> 和 <b>大运干支</b>。如果这步错了，后面的 K 线全都会错。
        <br>您可以直接点击文本框进行修改。
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        # 这里展示详细的排盘信息，包括大运
        edited_bazi = st.text_area(
            "排盘详细信息 (可编辑)", 
            value=st.session_state.bazi_cache, 
            height=400, # 加高高度，方便看大运
            help="请重点核对【大运排盘】区域的年份和干支。"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ 确认无误，开始演算", type="primary"):
                st.session_state.bazi_cache = edited_bazi 
                st.session_state.stage = 'result'
                st.rerun()
        with col2:
             st.markdown("<div style='padding-top: 10px; color: #888;'>点击确认后 AI 将基于上方数据生成 K 线</div>", unsafe_allow_html=True)

# === 状态二：展示结果 (Result Stage) ===
elif st.session_state.stage == 'result':
    if not api_key:
        st.error("⚠️ 缺少 API Key")
    else:
        with st.spinner("🚀 正在接入宇宙能量场，进行全周期量化..."):
            raw_data = get_ai_analysis(api_key, st.session_state.bazi_cache, birth_date.year)
            
            if "error" in raw_data:
                st.error(f"❌ 演算失败: {raw_data['error']}")
                if st.button("返回修改"):
                    st.session_state.stage = 'confirm'
                    st.rerun()
            else:
                timeline = raw_data.get("timeline", [])
                radar = raw_data.get("radar", {})
                ranking = raw_data.get("ranking", 50)
                df = pd.DataFrame(timeline)

                # 指标栏
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("全网排位", f"{ranking}%")
                with col2: st.metric("财富指数", radar.get('wealth', 0))
                with col3: st.metric("事业指数", radar.get('career', 0))
                with col4: st.metric("综合均分", int(df['close'].mean()) if not df.empty else 0)

                st.markdown("---")

                # K线图
                event_df = df[df['event'].notna() & (df['event'] != "")]
                fig_k = go.Figure(data=[go.Candlestick(
                    x=df['year'],
                    open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                    increasing_line_color='#00E676', decreasing_line_color='#FF3D00',
                    name="运势",
                    text=[f"<b>{row['year']} {row['ganzhi']}</b><br>{row['comment']}" for _, row in df.iterrows()],
                    hoverinfo='text+y'
                )])

                # 标注
                annotations = []
                for _, row in event_df.iterrows():
                    annotations.append(dict(
                        x=row['year'], y=row['high'], xref="x", yref="y",
                        text=f"🚩{row['event']}", showarrow=True, arrowhead=1, ax=0, ay=-40,
                        font=dict(color="#FFD700", size=12)
                    ))

                fig_k.update_layout(
                    title="人生量化走势图", template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=600,
                    annotations=annotations,
                    xaxis=dict(rangeslider=dict(visible=True), type="linear", gridcolor='rgba(255,255,255,0.1)'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                    dragmode='pan', hovermode='x unified'
                )
                st.plotly_chart(fig_k, use_container_width=True)
                
                # 雷达图
                categories = ['财富', '事业', '感情', '健康', '贵人']
                r_vals = [radar.get('wealth',50), radar.get('career',50), radar.get('love',50), radar.get('health',50), radar.get('social',50)]
                r_vals += [r_vals[0]]
                categories += [categories[0]]
                
                fig_r = go.Figure(go.Scatterpolar(r=r_vals, theta=categories, fill='toself', line_color='#FFD700'))
                fig_r.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(range=[0, 100])))
                
                c1, c2 = st.columns([1,2])
                with c1: st.markdown("#### 🎯 命局五维雷达"); st.plotly_chart(fig_r, use_container_width=True)
                with c2: 
                    st.markdown("#### 🗓️ 关键节点详情")
                    if not event_df.empty:
                        st.dataframe(event_df[['year', 'ganzhi', 'event', 'comment', 'close']], use_container_width=True, hide_index=True)

# === 状态零 ===
else:
    st.info("👈 请在左侧输入信息，并点击“排盘并核对”开始。")
