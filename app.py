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

# 2. የC-Market ዋጋን ማምጣት
def get_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        price = coffee.history(period="1d")['Close'].iloc[-1]
        return round(price, 2)
    except:
        return 0.0

# ገጹን ማዘጋጀት
st.set_page_config(page_title="Coffee Price Analysis", layout="wide")
st.title("☕ የቡና ዋጋ ትንተና (በ US Cents/lb)")

# የምንዛሬ ተመን በሳይድባር
st.sidebar.header("Currency Setup")
usd_to_etb = st.sidebar.number_input("የዛሬ የምንዛሬ ተመን (USD/ETB)", value=130.0, step=0.1)

# ዳታውን መጫን
df = load_data()
live_c = get_c_market()

# 3. የቡና አይነቶች
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]
selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

min_col = f"ETH_Min_{selected_type}"
pur_col = f"Pur_{selected_type}"

if min_col in df.columns and pur_col in df.columns:
    # ⚠️ ልወጣ (Conversion)
    # ECTA Min ቀድሞውኑ USC ስለሆነ ምንም አናባዛውም
    df['ECTA_Final'] = df[min_col]
    
    # ያንተ መግዣ (Birr/lb) ወደ USC ለመቀየር: (Birr / Rate) * 100
    df['Pur_Final'] = (df[pur_col] / usd_to_etb) * 100

    # ግራፍ
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['ECTA_Final'], name='ECTA Min (¢/lb)', line=dict(color='#2ecc71', width=3)))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Pur_Final'], name='Your Purchase (¢/lb)', line=dict(color='#e67e22', width=3)))
    
    # የኒውዮርክ መስመር
    fig.add_hline(y=live_c, line_dash="dash", line_color="#e74c3c", annotation_text=f"Live C-Market: {live_c}¢")

    fig.update_layout(title=f"የ {selected_type} ዋጋ ንጽጽር", yaxis_title="US Cents per lb")
    st.plotly_chart(fig, use_container_width=True)

    # Differential ትንተና
    latest_pur = df['Pur_Final'].iloc[-1]
    diff = latest_pur - live_c
    
    st.subheader("የገበያ ሁኔታ ማጠቃለያ")
    c1, c2, c3 = st.columns(3)
    c1.metric("ያንተ መግዣ (¢)", f"{round(latest_pur, 2)} ¢")
    c2.metric("C-Market (¢)", f"{live_c} ¢")
    c3.metric("ልዩነት (Diff)", f"{round(diff, 2)} ¢", delta=round(diff, 2), delta_color="inverse")

else:
    st.error("ኮለሞቹ በSheet ላይ አልተገኙም።")
