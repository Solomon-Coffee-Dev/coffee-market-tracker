import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. መረጃውን ከGoogle Sheet የማምጫ ሊንክ
# SHEET_ID በ Settings -> Secrets ውስጥ መኖሩን አረጋግጥ
SHEET_ID = st.secrets["SHEET_ID"]
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(url)

# ገጹን ማዘጋጀት
st.set_page_config(page_title="Coffee Price Tracker", layout="wide")
st.title("☕ የኢትዮጵያ ቡና ገበያ የዋጋ መከታተያ")

# ዳታውን መጫን
try:
    df = load_data()

    # 2. የቡና አይነቶችን መምረጫ (በSheetህ ላይ ባለው ስም መሰረት)
    coffee_types = [
        "Sidamo 2", "Yirg 2", "Limmu 2", "Sidamo 4", "Lekempti 4", 
        "Harar 4", "Djimma 4", "Lekempti 5", "Harar 5", "Djimma 5"
    ]
    
    selected_type = st.selectbox("የቡና አይነት ይምረጡ", coffee_types)

    # የኮለም ስሞችን መለየት
    min_col = f"ETH_Min_{selected_type}"
    pur_col = f"Pur_{selected_type}"

    if min_col in df.columns and pur_col in df.columns:
        # 3. የዋጋ ንጽጽር ግራፍ መሥራት
        fig = go.Figure()
        
        # የኢትዮጵያ ዝቅተኛ ኤክስፖርት ዋጋ (ECTA)
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df[min_col], 
            name='ECTA Min Price', 
            line=dict(color='#2ecc71', width=3)
        ))
        
        # ያንተ መግዣ ዋጋ (Purchase Price)
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df[pur_col], 
            name='Your Purchase Price', 
            line=dict(color='#e67e22', width=3, dash='dash')
        ))

        fig.update_layout(
            title=f"የ {selected_type} የዋጋ ለውጥ ንጽጽር",
            xaxis_title="ቀን",
            yaxis_title="ዋጋ",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 4. የቅርብ ጊዜ መረጃዎችን በሰንጠረዥ ማሳየት
        st.subheader("የቅርብ ጊዜ መረጃዎች (Last 5 Days)")
        st.table(df[['Date', min_col, pur_col]].tail(5))

    else:
        st.error(f"ስህተት፡ '{min_col}' ወይም '{pur_col}' የሚሉ ኮለሞች በGoogle Sheetህ ላይ አልተገኙም።")

except Exception as e:
    st.error(f"ዳታውን መጫን አልተቻለም። ስህተት፦ {e}")
