import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="AI Inventory PRO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 🎨 CLEAN PREMIUM UI
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background: #0B1220;
    color: #E5E7EB;
}

/* Title */
h1 {
    color: #60A5FA;
    font-weight: 800;
    letter-spacing: 0.5px;
}

/* Cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0A0F1C;
}

/* Inputs */
input {
    background: rgba(255,255,255,0.05) !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #3B82F6, #2563EB);
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #2563EB, #1D4ED8);
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Divider */
hr {
    border: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ DB
# =========================
DB = "inventory.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            company TEXT,
            model TEXT,
            type TEXT,
            color TEXT,
            stock REAL
        )
    """)
    conn.close()

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    return df

def save_data(df):
    conn = sqlite3.connect(DB)
    df.to_sql("inventory", conn, if_exists="replace", index=False)
    conn.close()

init_db()

# =========================
# 📥 UPLOAD
# =========================
uploaded_file = st.file_uploader("📦 העלה קובץ מלאי", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "חברה": "company",
        "דגם": "model",
        "סוג": "type",
        "צבע": "color",
        "מלאי": "stock"
    })

    for c in ["company", "model", "type", "color"]:
        df[c] = df[c].astype(str).str.strip()

    df["stock"] = pd.to_numeric(df["stock"], errors="coerce").fillna(0)

    save_data(df)
    st.success("✔ הנתונים נשמרו בהצלחה")

# =========================
# 📊 LOAD
# =========================
df = load_data()

if df.empty:
    st.warning("אין נתונים במערכת")
    st.stop()

# =========================
# 🧠 ENGINE
# =========================
df["SKU"] = (df["company"] + "-" + df["model"]).str.upper()

def status(x):
    if x == 0:
        return "🔴 אזל"
    elif x <= 2:
        return "🟠 נמוך"
    return "🟢 תקין"

df["סטטוס"] = df["stock"].apply(status)

# =========================
# 🚀 TITLE
# =========================
st.title("🚀 AI CONTROL NEXT PRO")

st.markdown("---")

# =========================
# 📊 KPI
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("פריטים", len(df))
c2.metric("סה״כ מלאי", int(df["stock"].sum()))
c3.metric("אזל", int((df["stock"] == 0).sum()))
c4.metric("נמוך", int((df["stock"] <= 2).sum()))

st.markdown("---")

# =========================
# 🔎 FILTERS (SIDEBAR)
# =========================
with st.sidebar:
    st.header("🔎 פילטרים")

    search = st.text_input("חיפוש SKU")

    company = st.multiselect("חברה", sorted(df["company"].unique()))
    type_f = st.multiselect("סוג", sorted(df["type"].unique()))
    color = st.multiselect("צבע", sorted(df["color"].unique()))

filtered = df.copy()

if search:
    filtered = filtered[filtered["SKU"].str.contains(search.upper(), na=False)]

if company:
    filtered = filtered[filtered["company"].isin(company)]

if type_f:
    filtered = filtered[filtered["type"].isin(type_f)]

if color:
    filtered = filtered[filtered["color"].isin(color)]

st.markdown("---")

# =========================
# 🚨 ALERTS
# =========================
col1, col2 = st.columns(2)

col1.error(f"🔴 אזל: {(filtered['stock'] == 0).sum()}")
col2.warning(f"🟠 נמוך: {(filtered['stock'] <= 2).sum()}")

st.markdown("---")

# =========================
# 📊 CHARTS
# =========================
left, right = st.columns(2)

with left:
    st.subheader("📦 מלאי לפי חברה")
    fig = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock",
        text="stock"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📊 סטטוס מלאי")
    pie_df = filtered.groupby("סטטוס")["stock"].sum().reset_index()
    fig2 = px.pie(pie_df, names="סטטוס", values="stock")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# =========================
# 📋 TABLE (PREMIUM STYLE)
# =========================
st.subheader("📋 טבלת מלאי")

def style(df):
    def color(row):
        if row["stock"] == 0:
            return ["background-color: rgba(255,0,0,0.15)"] * len(row)
        elif row["stock"] <= 2:
            return ["background-color: rgba(255,165,0,0.15)"] * len(row)
        return [""] * len(row)
    return df.style.apply(color, axis=1)

st.dataframe(
    style(filtered.sort_values("stock", ascending=False)),
    use_container_width=True,
    height=500
)

# =========================
# 🧠 INSIGHT
# =========================
if not filtered.empty:
    top = filtered.sort_values("stock", ascending=False).iloc[0]
    st.success(f"⭐ מוצר מוביל: {top['SKU']} ({int(top['stock'])})")