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
st.set_page_config(page_title="Coffee Price Tracker", layout="wide")
st.title("☕ የኢትዮጵያ ቡና ገበያ እና C-Market መከታተያ")

# ዳታውን መጫን
df = load_data()
live_c = get_c_market()

# በላይኛው ክፍል C-Marketን ማሳየት
st.metric("የዛሬ ኒውዮርክ C-Market (Live)", f"{live_c} ¢/lb")

# 3. የቡና አይነቶችን መምረጫ
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]
selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

min_col = f"ETH_Min_{selected_type}"
pur_col = f"Pur_{selected_type}"

if min_col in df.columns and pur_col in df.columns:
    # ግራፍ መሥራት
    fig = go.Figure()
    
    # ECTA ዝቅተኛ ዋጋ
    fig.add_trace(go.Scatter(x=df['Date'], y=df[min_col], name='ECTA Min Price', line=dict(color='#2ecc71', width=3)))
    
    # ያንተ መግዣ ዋጋ
    fig.add_trace(go.Scatter(x=df['Date'], y=df[pur_col], name='Your Purchase Price', line=dict(color='#e67e22', width=3, dash='dash')))
    
    fig.update_layout(title=f"የ {selected_type} የዋጋ ንጽጽር", xaxis_title="ቀን", yaxis_title="ዋጋ")
    st.plotly_chart(fig, use_container_width=True)

    # ሰንጠረዥ
    st.subheader("የቅርብ ጊዜ መረጃዎች")
    st.table(df[['Date', min_col, pur_col]].tail(5))
else:
    st.error("በሰንጠረዡ ላይ የኮለም ስሞች አልተገኙም።")
