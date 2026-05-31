import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# =========================
# 🎨 UI FIXED PREMIUM STYLE
# =========================
st.set_page_config(
    page_title="AI CONTROL NEXT",
    layout="wide"
)

st.markdown("""
<style>

/* ===== MAIN BACKGROUND (FIXED) ===== */
.stApp {
    background: linear-gradient(180deg, #0B1220 0%, #0F1B2D 100%);
    color: #E5E7EB;
}

/* ===== CONTAINER ===== */
.block-container {
    padding: 2rem 2.5rem;
}

/* ===== HEADINGS ===== */
h1 {
    color: #60A5FA !important;
    font-weight: 800;
}

h2, h3 {
    color: #E5E7EB !important;
}

/* ===== KPI CARDS (FIXED VISIBILITY) ===== */
[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 16px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}

/* ===== DATAFRAME (CLEAN GRID) ===== */
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.03);
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background-color: #0A0F1C;
}

/* ===== INPUTS ===== */
input, .stTextInput > div > div > input {
    background-color: rgba(255,255,255,0.05);
    color: white;
    border-radius: 10px;
}

/* ===== SELECT BOXES ===== */
div[data-baseweb="select"] {
    background-color: rgba(255,255,255,0.05);
}

/* ===== DIVIDERS ===== */
hr {
    border: 1px solid rgba(255,255,255,0.08);
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #3B82F6, #2563EB);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1rem;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #2563EB, #1D4ED8);
}

</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ DB
# =========================
DB = "inventory.db"

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
    return pd.read_sql("SELECT * FROM inventory", conn)

init_db()

# =========================
# 📥 DATA
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

    save(df)
    st.success("✔ נתונים נטענו למערכת")

# =========================
# 📊 LOAD
# =========================
df = load()

if df.empty:
    st.warning("אין נתונים")
    st.stop()

# =========================
# 🧠 ENGINE
# =========================
df["SKU"] = df["company"] + " " + df["model"]

df["סטטוס"] = df["stock"].apply(
    lambda x: "🔴 אזל" if x == 0 else ("🟠 נמוך" if x <= 2 else "🟢 תקין")
)

# =========================
# 🚀 HEADER
# =========================
st.title("🚀 AI CONTROL NEXT – מערכת מלאי חכמה")

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
# 🔎 SEARCH + FILTER
# =========================
col1, col2 = st.columns([1, 3])

with col1:
    search = st.text_input("🔎 חיפוש חכם")

    company = st.multiselect("חברה", sorted(df["company"].unique()))
    type_f = st.multiselect("סוג", sorted(df["type"].unique()))
    color = st.multiselect("צבע", sorted(df["color"].unique()))

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["SKU"].str.contains(search, case=False, na=False)
    ]

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
st.subheader("⚠ מצב מערכת")

a1, a2 = st.columns(2)

a1.error(f"🔴 אזל: {(filtered['stock'] == 0).sum()}")
a2.warning(f"🟠 נמוך: {(filtered['stock'] <= 2).sum()}")

st.markdown("---")

# =========================
# 📊 GRID DASHBOARD
# =========================
left, middle, right = st.columns([1.2, 1.2, 2.6])

with left:
    st.subheader("🔻 מלאי נמוך")
    st.dataframe(filtered.sort_values("stock").head(8), use_container_width=True)

with middle:
    st.subheader("📊 סטטוס")
    fig = px.pie(filtered, names="סטטוס", values="stock")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("📦 מלאי לפי חברה")
    fig2 = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# =========================
# 🧾 TABLE
# =========================
st.subheader("📋 טבלת מלאי")

st.dataframe(
    filtered.sort_values("stock", ascending=False),
    use_container_width=True
)

# =========================
# 🧠 INSIGHT
# =========================
if len(filtered) > 0:
    top = filtered.sort_values("stock", ascending=False).iloc[0]
    st.success(f"⭐ מוצר מוביל: {top['SKU']} ({int(top['stock'])})")