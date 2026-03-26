import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from io import BytesIO

# 1. ዳታ ማምጫ ከGoogle Sheet
SHEET_ID = st.secrets["SHEET_ID"]
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(url)
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    return df

# 2. የሲ-ማርኬት ዳታ ማምጫ (Safe Version)
@st.cache_data(ttl=3600)
def get_historic_c_market():
    try:
        coffee = yf.Ticker("KC=F")
        hist = coffee.history(period="3mo")
        if not hist.empty:
            hist = hist.reset_index()
            hist['Date'] = hist['Date'].dt.tz_localize(None).dt.date
            hist = hist.rename(columns={'Close': 'C-Market (¢)'})
            return hist[['Date', 'C-Market (¢)']]
        return pd.DataFrame(columns=['Date', 'C-Market (¢)'])
    except:
        return pd.DataFrame(columns=['Date', 'C-Market (¢)'])

st.set_page_config(page_title="Coffee Market Dashboard", layout="wide")
st.title("☕ የቡና ገበያ የተቀናጀ ትንተና")

# Sidebar
usd_to_etb = st.sidebar.number_input("የዛሬ የምንዛሬ ተመን (USD/ETB)", value=130.0, step=0.1)

df = load_data()
c_market_hist = get_historic_c_market()

# Live C-Market Price Metric
if not c_market_hist.empty:
    live_c = round(c_market_hist['C-Market (¢)'].iloc[-1], 2)
    st.metric("የዛሬ ኒውዮርክ C-Market (Live)", f"{live_c} ¢/lb")
else:
    live_c = 0.0
    st.warning("የኒውዮርክ C-Market መረጃ ለጊዜው አልተገኘም (ገበያ ዝግ ሊሆን ይችላል)።")

# 3. የዕለቱ ማጠቃለያ ሰንጠረዥ
st.subheader("📊 የ10ሩም የቡና አይነቶች የዛሬ ንጽጽር (¢/lb)")
summary_data = []
coffee_types = ["Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"]

for c_type in coffee_types:
    min_col = f"ETH_Min_{c_type}"
    pur_col = f"Pur_{c_type}"
    if min_col in df.columns and pur_col in df.columns:
        ecta_val = df[min_col].iloc[-1]
        pur_usc = round((df[pur_col].iloc[-1] / usd_to_etb) * 100, 2)
        summary_data.append({
            "የቡና አይነት": c_type,
            "C-Market (¢)": live_c,
            "ECTA (¢)": round(ecta_val, 2),
            "Local Purchase Price (¢)": pur_usc,
            "ECTA vs Local Purchase": round(ecta_val - pur_usc, 2),
            "ECTA vs C-Market": round(ecta_val - live_c, 2)
        })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df.style.format("{:.2f}", subset=summary_df.columns[1:]), use_container_width=True, hide_index=True)

st.divider()

# 4. የታሪካዊ መረጃ ግራፍ
st.subheader("📈 የረጅም ጊዜ የዋጋ እንቅስቃሴ (Historic Trend Analysis)")
selected_type = st.selectbox("ዝርዝር መረጃ ለማየት አይነት ይምረጡ", coffee_types)

min_col_g = f"ETH_Min_{selected_type}"
pur_col_g = f"Pur_{selected_type}"

if min_col_g in df.columns and pur_col_g in df.columns:
    df_plot = df.copy()
    df_plot['Local_USC'] = (df_plot[pur_col_g] / usd_to_etb) * 100
    
    fig = go.Figure()
    if not c_market_hist.empty:
        fig.add_trace(go.Scatter(x=c_market_hist['Date'], y=c_market_hist['C-Market (¢)'], name='NY C-Market', line=dict(color='#e74c3c', width=2)))
    
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot[min_col_g], name='ECTA Min (¢)', line=dict(color='#2ecc71', width=3)))
    fig.add_trace(go.Scatter(x=df_plot['Date'], y=df_plot['Local_USC'], name='Local Purchase (¢)', line=dict(color='#e67e22', width=3, dash='dot')))
    
    fig.update_layout(title=f"የ {selected_type} የዋጋ ታሪክ", xaxis_title="ቀን", yaxis_title="US Cents/lb", hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # 5. ዝርዝር የታሪክ ሰንጠረዥ ከዳውንሎድ ቁልፍ ጋር
    st.subheader(f"📋 የ {selected_type} ዝርዝር የታሪክ ሰንጠረዥ")
    
    local_data = df_plot[['Date', min_col_g, 'Local_USC']].copy()
    combined_historic = pd.merge(local_data, c_market_hist, on='Date', how='left')
    combined_historic = combined_historic[['Date', 'C-Market (¢)', min_col_g, 'Local_USC']]
    combined_historic.columns = ['ቀን', 'C-Market (¢)', 'ECTA Min (¢)', 'Local Purchase (¢)']
    combined_historic['ECTA vs Local'] = combined_historic['ECTA Min (¢)'] - combined_historic['Local Purchase (¢)']
    combined_historic['ECTA vs C-Market'] = combined_historic['ECTA Min (¢)'] - combined_historic['C-Market (¢)']
    combined_historic = combined_historic.sort_values(by='ቀን', ascending=False)

    # 📥 የ Excel ዳውንሎድ ተግባር
    def to_excel(df_to_dl):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_to_dl.to_excel(writer, index=False, sheet_name='Price_History')
        return output.getvalue()

    excel_data = to_excel(combined_historic)
    st.download_button(
        label="📥 Download as Excel",
        data=excel_data,
        file_name=f"{selected_type}_Price_History.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.dataframe(combined_historic.style.format({
        'C-Market (¢)': '{:.2f}', 'ECTA Min (¢)': '{:.2f}', 'Local Purchase (¢)': '{:.2f}',
        'ECTA vs Local': '{:.2f}', 'ECTA vs C-Market': '{:.2f}'
    }), use_container_width=True, hide_index=True)
