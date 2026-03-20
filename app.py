import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. የGoogle Sheet መረጃ (የራስህን ID እዚህ አስገባ)
SHEET_ID = '1n4O2iorn6mRcJfsIJHowpGjz3YjA0ZW42yzt2gLCJ5A' 
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_all_data():
    c_market = yf.Ticker("KC=F").history(period="1mo")
    eth_data = pd.read_csv(SHEET_URL)
    eth_data['Date'] = pd.to_datetime(eth_data['Date'])
    return c_market, eth_data

st.set_page_config(page_title="Ethiopia Coffee Spread Tracker", layout="wide")
st.title("☕ የተሟላ የኢትዮጵያ ቡና ገበያ እና የSpread ትንተና")

try:
    c_df, eth_df = load_all_data()
    curr_c = c_df['Close'].iloc[-1]
    last_row = eth_df.iloc[-1]

    # --- ክፍል 1፡ የወቅቱ ዋጋዎች (Current Prices) ---
    st.subheader("📊 የወቅቱ ዝቅተኛ መነሻ ዋጋዎች")
    # ዋናዎቹ 4
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Global C-Market", f"{curr_c:.2f}¢")
    m2.metric("Sidamo G2", f"{last_row['ETH_Min_Sidamo 2']:.2f}¢")
    m3.metric("Yirgachefe G2", f"{last_row['ETH_Min_Yirg 2']:.2f}¢")
    m4.metric("Limmu G2", f"{last_row['ETH_Min_Limmu 2']:.2f}¢")

    # --- ክፍል 2፡ የSpread (ልዩነት) ትንተና ---
    st.divider()
    st.subheader("⚖️ የSpread ትንተና (የሀገር ውስጥ ዋጋ - የአለም ገበያ)")
    
    # 10ሩም የቡና አይነቶች ዝርዝር
    all_coffee = {
        'ETH_Min_Sidamo 2': 'Sidamo G2',
        'ETH_Min_Yirg 2': 'Yirgachefe G2',
        'ETH_Min_Limmu 2': 'Limmu G2',
        'ETH_Min_Sidamo 4': 'Sidamo G4',
        'ETH_Min_Lekempti 4': 'Lekempti G4',
        'ETH_Min_Harar 4': 'Harar G4',
        'ETH_Min_Djimma 4': 'Djimma G4',
        'ETH_Min_Lekempti 5': 'Lekempti G5',
        'ETH_Min_Harar 5': 'Harar G5',
        'ETH_Min_Djimma 5': 'Djimma G5'
    }

    # Spread ለማሳየት በ3 ረድፍ ከፋፍለን እናስቀምጣቸው
    s_cols = st.columns(4)
    idx = 0
    for col_name, label in all_coffee.items():
        if col_name in eth_df.columns:
            spread_val = last_row[col_name] - curr_c
            s_cols[idx % 4].metric(f"{label} Spread", f"{spread_val:.2f}¢", delta=f"{spread_val:.1f}")
            idx += 1

    # --- ክፍል 3፡ የተቀናጀ ግራፍ ---
    st.divider()
    fig = go.Figure()
    # የአለም ገበያ መስመር
    fig.add_trace(go.Scatter(x=c_df.index, y=c_df['Close'], name="C-Market", line=dict(width=4, color='black')))
    
    # የኢትዮጵያ ቡናዎች መስመር
    for col_name, label in all_coffee.items():
        if col_name in eth_df.columns:
            fig.add_trace(go.Scatter(x=eth_df['Date'], y=eth_df[col_name], name=label))

    fig.update_layout(height=600, hovermode="x unified", title="የ10ሩም የቡና አይነቶች የዋጋ ንጽጽር")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"ስህተት ተፈጥሯል! እባክህ በGoogle Sheet ላይ ያሉት የርዕስ ስሞች ከኮዱ ጋር አንድ አይነት መሆናቸውን አረጋግጥ። ዝርዝር፦ {e}")