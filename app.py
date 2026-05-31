import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# =========================
# 🎨 NASA CONTROL UI
# =========================
st.set_page_config(
    page_title="NASA INVENTORY CONTROL",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
body {
    background-color: #0B0F19;
    color: #E5E7EB;
}

.stApp {
    background-color: #0B0F19;
}

h1, h2, h3 {
    color: #38BDF8;
    font-family: Arial;
    letter-spacing: 1px;
}

div[data-testid="metric-container"] {
    background-color: #111827;
    border: 1px solid #1F2937;
    padding: 12px;
    border-radius: 10px;
}

.stDataFrame {
    border: 1px solid #1F2937;
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ CLOUD DATABASE LAYER
# =========================
DB = "cloud_inventory.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            company TEXT,
            model TEXT,
            type TEXT,
            color TEXT,
            stock REAL
        )
    """)
    conn.commit()
    conn.close()

def save(df):
    conn = sqlite3.connect(DB)
    df.to_sql("inventory", conn, if_exists="replace", index=False)
    conn.close()

def load():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    return df

init_db()

# =========================
# 📥 DATA INGEST
# =========================
uploaded_file = st.file_uploader("📡 UPLOAD INVENTORY DATA", type=["xlsx"])

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

    save(df)
    st.success("🟢 DATA LOADED INTO CLOUD SYSTEM")

# =========================
# 📊 LOAD SYSTEM STATE
# =========================
df = load()

if df.empty:
    st.warning("⚠ NO DATA IN SYSTEM")
    st.stop()

# =========================
# 🧠 ENGINE LAYER
# =========================
df["SKU"] = df["company"] + " " + df["model"]

def status(x):
    if x == 0:
        return "🔴 CRITICAL"
    elif x <= 2:
        return "🟠 WARNING"
    return "🟢 OK"

df["status"] = df["stock"].apply(status)

# =========================
# 🚀 HEADER (MISSION CONTROL)
# =========================
st.title("🚀 NASA INVENTORY CONTROL CENTER")

col1, col2, col3, col4 = st.columns(4)

col1.metric("TOTAL ASSETS", len(df))
col2.metric("TOTAL STOCK", int(df["stock"].sum()))
col3.metric("CRITICAL", int((df["stock"] == 0).sum()))
col4.metric("LOW STOCK", int((df["stock"] <= 2).sum()))

st.divider()

# =========================
# 🔎 SEARCH
# =========================
search = st.text_input("🔎 SEARCH SYSTEM")

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["SKU"].str.contains(search, case=False, na=False) |
        filtered["company"].str.contains(search, case=False, na=False) |
        filtered["model"].str.contains(search, case=False, na=False)
    ]

# =========================
# 🎛 CONTROL FILTERS
# =========================
colf1, colf2, colf3 = st.columns(3)

with colf1:
    company = st.multiselect("COMPANY", sorted(filtered["company"].unique()))

with colf2:
    type_f = st.multiselect("TYPE", sorted(filtered["type"].unique()))

with colf3:
    color = st.multiselect("COLOR", sorted(filtered["color"].unique()))

if company:
    filtered = filtered[filtered["company"].isin(company)]

if type_f:
    filtered = filtered[filtered["type"].isin(type_f)]

if color:
    filtered = filtered[filtered["color"].isin(color)]

st.divider()

# =========================
# 🚨 ALERT SYSTEM
# =========================
critical = filtered[filtered["stock"] == 0]
warning = filtered[filtered["stock"] <= 2]

if len(critical) > 0:
    st.error(f"🚨 CRITICAL FAILURE: {len(critical)} ITEMS OUT OF STOCK")

if len(warning) > 0:
    st.warning(f"⚠ WARNING: {len(warning)} LOW STOCK ITEMS")

# =========================
# 🧾 CONTROL TABLE
# =========================
st.subheader("📡 LIVE INVENTORY GRID")

st.dataframe(
    filtered.sort_values("stock", ascending=False),
    use_container_width=True
)

# =========================
# 📊 ANALYTICS PANEL
# =========================
colg1, colg2 = st.columns(2)

with colg1:
    st.subheader("📈 STOCK BY COMPANY")

    fig1 = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )

    st.plotly_chart(fig1, use_container_width=True)

with colg2:
    st.subheader("🥧 STATUS DISTRIBUTION")

    fig2 = px.pie(
        filtered,
        names="status",
        values="stock"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 🧠 FINAL INSIGHT
# =========================
st.divider()

if len(filtered) > 0:
    top = filtered.sort_values("stock", ascending=False).iloc[0]

    st.success(f"🛰 PRIMARY ASSET: {top['SKU']} | STOCK: {int(top['stock'])}")