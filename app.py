import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# 1. መረጃውን ከGoogle Sheet ማምጣት
SHEET_ID = st.secrets["SHEET_ID"]
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(url)

# 2. የሲ-ማርኬት ዋጋ (የመጨረሻውን 5 ቀን ዳታ አይቶ የመጨረሻውን ዋጋ ይወስዳል)
def get_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        hist = coffee.history(period="5d")
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            return round(price, 2)
        return 0.0
    except:
        return 0.0

st.set_page_config(page_title="Coffee Market Dashboard", layout="wide")
st.title("☕ የቡና ገበያ አጠቃላይ ትንተና")

# Sidebar - የምንዛሬ ተመን
st.sidebar.header("Currency Setup")
usd_to_etb = st.sidebar.number_input("የዛሬ የምንዛሬ ተመን (USD/ETB)", value=130.0, step=0.1)

df = load_data()
live_c = get_c_market()

# Live C-Market Price
st.subheader(f"የዛሬ ኒውዮርክ C-Market (Live): {live_c} ¢/lb")

# 3. ሁሉንም የቡና አይነቶች የሚያሳይ ማጠቃለያ ሰንጠረዥ
st.markdown("### 📊 የሁሉም የቡና አይነቶች ማጠቃለያ (በ USC/lb)")

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

# 4. ዝርዝር ግራፍ (The Figure Section)
st.subheader("📈 ዝርዝር የዋጋ ግራፍ (Trend Analysis)")
selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

min_col = f"ETH_Min_{selected_type}"
pur_col = f"Pur_{selected_type}"

if min_col in df.columns and pur_col in df.columns:
    # ዳታውን ማዘጋጀት
    df_plot = df.copy()
    df_plot['Pur_Final'] = (df_plot[pur_col] / usd_to_etb) * 100
    df_plot['ECTA_Final'] = df_plot[min_col]

    # ግራፍ (Figure) መሥራት
    fig = go.Figure()
    
    # ECTA Min Price
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], 
        y=df_plot['ECTA_Final'], 
        name='ECTA Min (¢/lb)', 
        line=dict(color='#2ecc71', width=3)
    ))
    
    # Your Purchase
    fig.add_trace(go.Scatter(
        x=df_plot['Date'], 
        y=df_plot['Pur_Final'], 
        name='Your Purchase (¢/lb)', 
        line=dict(color='#e67e22', width=3, dash='dot')
    ))
    
    # Live C-Market Line
    fig.add_hline(y=live_c, line_dash="dash", line_color="#e74c3c", 
                  annotation_text=f"Live C-Market: {live_c}¢")

    fig.update_layout(
        title=f"የ {selected_type} የዋጋ ለውጥ ታሪክ",
        xaxis_title="ቀን",
        yaxis_title="US Cents per lb",
        hovermode="x unified",
        template="plotly_dark",
        height=500
    )
    
    # ግራፉን ማሳየት
    st.plotly_chart(fig, use_container_width=True)

    # የቅርብ ጊዜ ውጤት Metrics
    c1, c2, c3 = st.columns(3)
    latest_pur = df_plot['Pur_Final'].iloc[-1]
    diff_val = latest_pur - live_c
    
    c1.metric("ያንተ መግዣ (¢)", f"{round(latest_pur, 2)} ¢")
    c2.metric("C-Market (¢)", f"{live_c} ¢")
    c3.metric("ልዩነት (Diff)", f"{round(diff_val, 2)} ¢", delta=round(diff_val, 2), delta_color="inverse")
