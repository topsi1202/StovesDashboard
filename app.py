import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# =========================
# ⚙️ CONFIG
# =========================
st.set_page_config(
    page_title="AI CONTROL NEXT",
    layout="wide"
)

# =========================
# 🎨 CLEAN UI
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
    color: #38BDF8;
    font-weight: 800;
}

/* Metrics */
[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1F2937;
    border-radius: 14px;
    padding: 14px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0A0F1C;
}

/* Inputs */
input {
    background: #111827 !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Buttons */
.stButton > button {
    background: #38BDF8;
    color: #0B1220;
    font-weight: 700;
    border-radius: 10px;
    border: none;
}

/* Table */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
}

/* Divider */
hr {
    border: 1px solid #1F2937;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ DATABASE
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
    st.success("✔ הנתונים נשמרו")

# =========================
# 📊 LOAD DATA
# =========================
df = load_data()

if df.empty:
    st.warning("אין נתונים")
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
# 🚀 HEADER
# =========================
st.title("🚀 AI CONTROL NEXT")

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
# 🔎 FILTERS
# =========================
with st.sidebar:
    st.header("🔎 פילטרים")

    search = st.text_input("חיפוש SKU")

    company = st.multiselect("חברה", df["company"].unique())
    type_f = st.multiselect("סוג", df["type"].unique())
    color = st.multiselect("צבע", df["color"].unique())

filtered = df.copy()

if search:
    filtered = filtered[filtered["SKU"].str.contains(search.upper(), na=False)]

if company:
    filtered = filtered[filtered["company"].isin(company)]

if type_f:
    filtered = filtered[filtered["type"].isin(type_f)]

if color:
    filtered = filtered[filtered["color"].isin(color)]

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
    fig2 = px.pie(
        filtered.groupby("סטטוס")["stock"].sum().reset_index(),
        names="סטטוס",
        values="stock"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# =========================
# 📋 TABLE
# =========================
st.subheader("📋 מלאי")

st.dataframe(
    filtered.sort_values("stock", ascending=False),
    use_container_width=True
)

# =========================
# 🧠 INSIGHT
# =========================
if not filtered.empty:
    top = filtered.sort_values("stock", ascending=False).iloc[0]
    st.success(f"⭐ מוצר מוביל: {top['SKU']} ({int(top['stock'])})")