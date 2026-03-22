import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. መረጃውን ከGoogle Sheet የማምጫ ሊንክ
SHEET_ID = st.secrets["SHEET_ID"]
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(url)

# 2. የC-Market ዋጋን ከ Yahoo Finance ማምጣት
def get_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        price = coffee.history(period="1d")['Close'].iloc[-1]
        return round(price, 2)
    except:
        return 185.0 # መረጃው ካልመጣ እንደ አማካኝ ይውሰድ

# ገጹን ማዘጋጀት
st.set_page_config(page_title="Coffee Market Analysis", layout="wide")
st.title("☕ የተቀናጀ የቡና ዋጋ ንጽጽር (USD Analysis)")

# የጎን ሳጥን (Sidebar) ለምንዛሬ
st.sidebar.header("የምንዛሬ ማስተካከያ")
usd_to_etb = st.sidebar.number_input("1 USD በስንት ብር? (Exchange Rate)", value=130.0, step=0.1)

# ዳታውን መጫን
df = load_data()
live_c = get_c_market()

col1, col2 = st.columns(2)
with col1:
    st.metric("የዛሬ ኒውዮርክ C-Market", f"${live_c} /lb")
with col2:
    st.info(f"የምንዛሬ ተመን፦ 1 USD = {usd_to_etb} ETB")

# 3. የቡና አይነቶችን መምረጫ
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]
selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

min_col = f"ETH_Min_{selected_type}"
pur_col = f"Pur_{selected_type}"

if min_col in df.columns and pur_col in df.columns:
    # ⚠️ የመግዣ ዋጋን (ብር) ወደ ዶላር መቀየር (ETB / Exchange Rate)
    # ማሳሰቢያ፡ ኒውዮርክ በ 'lb' ስለሆነ ብሩን ወደ USD ቀይረን በ 'lb' እናስቀምጠዋለን
    df['Purchase_USD'] = df[pur_col] / usd_to_etb

    # ንጽጽር ግራፍ (ሁሉም በ USD)
    fig = go.Figure()
    # የኢትዮጵያ ዝቅተኛ ዋጋ (በ USD ነው ያለው)
    fig.add_trace(go.Scatter(x=df['Date'], y=df[min_col], name='ECTA Minimum (USD)', line=dict(color='green', width=3)))
    # ያንተ መግዣ ዋጋ (ወደ USD የተቀየረ)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Purchase_USD'], name='Your Purchase (USD Equivalent)', line=dict(color='orange', width=3, dash='dot')))
    # የኒውዮርክ ዋጋ (እንደ መስመር)
    fig.add_hline(y=live_c, line_dash="dash", line_color="red", annotation_text="Today's C-Market")

    fig.update_layout(title=f"የ {selected_type} የዋጋ ንጽጽር በ USD", xaxis_title="ቀን", yaxis_title="ዋጋ በ USD / lb")
    st.plotly_chart(fig, use_container_width=True)

    # የትርፍ/ኪሳራ ግምት (Margin)
    current_min = df[min_col].iloc[-1]
    current_pur_usd = df['Purchase_USD'].iloc[-1]
    margin = current_min - current_pur_usd
    
    st.subheader("የገበያ ትንተና (Current Snapshot)")
    m1, m2, m3 = st.columns(3)
    m1.metric("ዝቅተኛ ኤክስፖርት ዋጋ", f"${current_min}")
    m2.metric("ያንተ መግዣ (በUSD)", f"${round(current_pur_usd, 2)}")
    m3.metric("ልዩነት (Margin)", f"${round(margin, 2)}", delta=f"{round(margin, 2)}")

else:
    st.error("በሰንጠረዡ ላይ የኮለም ስሞች አልተገኙም። እባክህ የSheet ርዕሶችን አረጋግጥ።")
