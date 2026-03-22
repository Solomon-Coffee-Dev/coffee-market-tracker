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

# 2. የሲ-ማርኬት ዋጋ
def get_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        hist = coffee.history(period="5d")
        if not hist.empty:
            return round(hist['Close'].iloc[-1], 2)
        return 0.0
    except:
        return 0.0

st.set_page_config(page_title="Coffee Market Comparison", layout="wide")
st.title("☕ የቡና ገበያ የተቀናጀ ንጽጽር")

# Sidebar
st.sidebar.header("ማስተካከያ")
usd_to_etb = st.sidebar.number_input("የምንዛሬ ተመን (USD/ETB)", value=155.0, step=0.1)

df = load_data()
live_c = get_c_market()

st.metric("የዛሬ ኒውዮርክ C-Market (Live)", f"{live_c} ¢/lb")

# 3. ሁሉንም 10 አይነቶች በአንድ ላይ የሚያነጻጽር ሰንጠረዥ
st.subheader("📊 አጠቃላይ የ10ሩም የቡና አይነቶች ንጽጽር (በ USC/lb)")

summary_data = []
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]

for c_type in coffee_types:
    min_col = f"ETH_Min_{c_type}"
    pur_col = f"Pur_{c_type}"
    
    if min_col in df.columns and pur_col in df.columns:
        ecta_val = df[min_col].iloc[-1]
        pur_birr = df[pur_col].iloc[-1]
        
        # ልወጣ እና ወደ 2 ዴሲማል መጠቅለል
        pur_usc = round((pur_birr / usd_to_etb) * 100, 2)
        
        # ልዩነቶች (Differentials)
        ecta_vs_pur = round(ecta_val - pur_usc, 2)
        ecta_vs_c = round(ecta_val - live_c, 2)
        
        summary_data.append({
            "የቡና አይነት": c_type,
            "C-Market (¢)": live_c, # አዲሱ ኮለም እዚህ ተጨመረ
            "ECTA (¢)": round(ecta_val, 2),
            "Local Purchase Price (¢)": pur_usc,
            "ECTA vs Local Purchase": ecta_vs_pur,
            "ECTA vs C-Market": ecta_vs_c
        })

summary_df = pd.DataFrame(summary_data)

# ሰንጠረዡን በውበት እና በ2 ዴሲማል ለማሳየት
def color_diff(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

# ቁጥሮቹን በ2 ዴሲማል ፎርማት ማድረግ
formatted_df = summary_df.style.format({
    "C-Market (¢)": "{:.2f}",
    "ECTA (¢)": "{:.2f}",
    "Local Purchase Price (¢)": "{:.2f}",
    "ECTA vs Local Purchase": "{:.2f}",
    "ECTA vs C-Market": "{:.2f}"
}).applymap(color_diff, subset=['ECTA vs Local Purchase', 'ECTA vs C-Market'])

st.dataframe(formatted_df, use_container_width=True, hide_index=True)

st.divider()

# 4. ዝርዝር ግራፍ (Figure)
st.subheader("📈 ዝርዝር የዋጋ እንቅስቃሴ (Trend)")
selected_type = st.selectbox("አንድ አይነት መርጠው በግራፍ ይመልከቱ", coffee_types)

min_col_g = f"ETH_Min_{selected_type}"
pur_col_g = f"Pur_{selected_type}"

if min_col_g in df.columns and pur_col_g in df.columns:
    df_plot = df.copy()
    # ወደ USC መቀየር እና በ 2 ዴሲማል ማስቀመጥ
    df_plot['Pur_USC'] = round((df_plot[pur_col_g] / usd_to_etb) * 100, 2)
    df_plot['ECTA_Final'] = round(df_plot[min_col_g], 2)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['ECTA_Final'], name='ECTA Min (¢)', line=dict(color='#2ecc71', width=3)))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Pur_USC'], name='Local Purchase (¢)', line=dict(color='#e67e22', width=3, dash='dot')))
    fig.add_hline(y=live_c, line_dash="dash", line_color="#e74c3c", annotation_text=f"C-Market: {live_c}¢")
    
    fig.update_layout(
        title=f"የ {selected_type} የዋጋ ታሪክ", 
        xaxis_title="ቀን", 
        yaxis_title="US Cents/lb", 
        template="plotly_white",
        yaxis=dict(tickformat=".2f")
    )
    st.plotly_chart(fig, use_container_width=True)
