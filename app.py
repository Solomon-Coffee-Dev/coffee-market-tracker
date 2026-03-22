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
        return 0.0

# ገጹን ማዘጋጀት
st.set_page_config(page_title="Coffee Price in US Cents", layout="wide")
st.title("☕ የቡና ዋጋ ንጽጽር (በ US Cents/lb)")

# የምንዛሬ ተመን በሳይድባር
st.sidebar.header("ማስተካከያ")
usd_to_etb = st.sidebar.number_input("1 USD በስንት ብር? (Exchange Rate)", value=130.0, step=0.1)

# ዳታውን መጫን
df = load_data()
live_c = get_c_market()

# 3. የቡና አይነቶችን መምረጫ
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]
selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

min_col = f"ETH_Min_{selected_type}"
pur_col = f"Pur_{selected_type}"

if min_col in df.columns and pur_col in df.columns:
    # ⚠️ ብርን ወደ US Cents/lb የመቀየር ሒሳብ
    # 1. ብር / የምንዛሬ ተመን = USD per kg
    # 2. (USD per kg / 2.20462) * 100 = US Cents per lb
    df['Pur_Cents'] = (df[pur_col] / usd_to_etb / 2.20462) * 100
    
    # የኢትዮጵያ ዝቅተኛ ዋጋ ቀድሞውኑ በUSD/lb ከሆነ ወደ ሴንት ለመቀየር በ 100 ማባዛት
    df['Min_Cents'] = df[min_col] * 100

    # ግራፍ መስራት
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Min_Cents'], name='ECTA Min (Cents/lb)', line=dict(color='#2ecc71', width=3)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Pur_Cents'], name='Your Purchase (Cents/lb)', line=dict(color='#e67e22', width=3)))
    
    # የዛሬ የኒውዮርክ ዋጋ መስመር
    fig.add_hline(y=live_c, line_dash="dash", line_color="#e74c3c", annotation_text=f"Live C-Market: {live_c}¢")

    fig.update_layout(title=f"የ {selected_type} ዋጋ ንጽጽር (በ US Cents)", yaxis_title="US Cents per lb")
    st.plotly_chart(fig, use_container_width=True)

    # የዋጋ ልዩነት (Differential)
    latest_pur = df['Pur_Cents'].iloc[-1]
    diff = latest_pur - live_c
    
    col1, col2, col3 = st.columns(3)
    col1.metric("ያንተ መግዣ (Cents)", f"{round(latest_pur, 2)} ¢")
    col2.metric("C-Market", f"{live_c} ¢")
    col3.metric("ልዩነት (Diff)", f"{round(diff, 2)} ¢", delta=round(diff, 2), delta_color="inverse")

else:
    st.error("በሰንጠረዡ ላይ የኮለም ስሞች አልተገኙም።")
