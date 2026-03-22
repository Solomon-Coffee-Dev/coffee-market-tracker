import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. ዳታ ማምጫ
SHEET_ID = st.secrets["SHEET_ID"]
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(url)

# 2. የሲ-ማርኬት ዋጋ (የተሻሻለ)
def get_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        # ገበያው ዝግ ቢሆን እንኳ የመጨረሻውን ዋጋ እንዲያመጣ period="5d" እንጠቀማለን
        hist = coffee.history(period="5d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            return round(price, 2)
        return 0.0
    except:
        return 0.0

st.set_page_config(page_title="Coffee Market Analysis", layout="wide")
st.title("☕ የቡና ገበያ አጠቃላይ ትንተና")

# sidebar
usd_to_etb = st.sidebar.number_input("የምንዛሬ ተመን (USD/ETB)", value=130.0, step=0.1)

df = load_data()
live_c = get_c_market()

# Metrics
st.metric("የዛሬ ኒውዮርክ C-Market (Live)", f"{live_c} ¢/lb")

# 3. ሁሉንም አይነቶች የሚያሳይ ማጠቃለያ ሰንጠረዥ
st.subheader("📊 የሁሉም የቡና አይነቶች ማጠቃለያ (በ USC/lb)")

summary_data = []
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]

for c_type in coffee_types:
    min_col = f"ETH_Min_{c_type}"
    pur_col = f"Pur_{c_type}"
    
    if min_col in df.columns and pur_col in df.columns:
        latest_min = df[min_col].iloc[-1]
        latest_pur_birr = df[pur_col].iloc[-1]
        # ወደ USC መቀየር
        pur_usc = round((latest_pur_birr / usd_to_etb) * 100, 2)
        diff = round(pur_usc - live_c, 2)
        
        summary_data.append({
            "የቡና አይነት": c_type,
            "ECTA Min (¢)": latest_min,
            "ያንተ መግዣ (¢)": pur_usc,
            "ልዩነት ከ C-Market (¢)": diff
        })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()

# 4. ነጠላ ግራፍ መመልከቻ (የድሮው)
selected_type = st.selectbox("ዝርዝር ግራፍ ለማየት እዚህ ይምረጡ", coffee_types)
# ... (ቀሪው የግራፍ ኮድ ከላይ በሰጠሁህ መሰረት ይቀጥላል)
