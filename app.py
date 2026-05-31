import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# =========================
# 🎨 UI CONFIG
# =========================
st.set_page_config(
    page_title="מערכת מלאי פרימיום",
    layout="wide"
)

st.markdown("""
<style>
/* רקע כללי נקי */
.block-container {
    padding: 2rem 2.5rem;
    background-color: #F6F8FC;
}

/* כותרות */
h1 {
    font-size: 34px;
    font-weight: 700;
    color: #111827;
}

h2, h3 {
    color: #1F2937;
}

/* KPI Cards */
[data-testid="metric-container"] {
    background: white;
    border-radius: 14px;
    padding: 14px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E5E7EB;
}

/* Buttons */
.stButton > button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    border: none;
}

.stButton > button:hover {
    background-color: #1D4ED8;
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
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    return df

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
    st.success("✔ הנתונים נשמרו במערכת")

# =========================
# 📊 LOAD
# =========================
df = load()

if df.empty:
    st.warning("אין נתונים עדיין")
    st.stop()

# =========================
# 🧠 LOGIC
# =========================
df["SKU"] = df["company"] + " " + df["model"]

def status(x):
    if x == 0:
        return "🔴 אזל"
    elif x <= 2:
        return "🟠 נמוך"
    return "🟢 תקין"

df["סטטוס"] = df["stock"].apply(status)

# =========================
# 🏠 HEADER
# =========================
st.title("📦 מערכת ניהול מלאי – גרסת פרימיום")

st.markdown("### סקירה כללית של המלאי בזמן אמת")

st.divider()

# =========================
# 📊 KPI
# =========================
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("פריטים", len(df))
c2.metric("סה״כ מלאי", int(df["stock"].sum()))
c3.metric("אזל", int((df["stock"] == 0).sum()))
c4.metric("נמוך", int((df["stock"] <= 2).sum()))
c5.metric("דגמים", df["model"].nunique())

st.divider()

# =========================
# 🔎 SEARCH + FILTER AREA
# =========================
col1, col2 = st.columns([2, 3])

with col1:
    search = st.text_input("🔎 חיפוש חכם")

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["SKU"].str.contains(search, case=False, na=False)
    ]

with col2:
    st.markdown("### פילטרים")

    f1, f2, f3 = st.columns(3)

    with f1:
        company = st.multiselect("חברה", sorted(filtered["company"].unique()))

    with f2:
        type_f = st.multiselect("סוג", sorted(filtered["type"].unique()))

    with f3:
        color = st.multiselect("צבע", sorted(filtered["color"].unique()))

if company:
    filtered = filtered[filtered["company"].isin(company)]

if type_f:
    filtered = filtered[filtered["type"].isin(type_f)]

if color:
    filtered = filtered[filtered["color"].isin(color)]

st.divider()

# =========================
# 🚨 ALERTS
# =========================
low = filtered[filtered["stock"] <= 2]
zero = filtered[filtered["stock"] == 0]

if len(zero) > 0:
    st.error(f"❌ אזל מהמלאי: {len(zero)} מוצרים")

if len(low) > 0:
    st.warning(f"⚠️ מלאי נמוך: {len(low)} מוצרים")

# =========================
# 📋 TABLE
# =========================
st.subheader("📦 נתוני מלאי")

st.dataframe(
    filtered.sort_values("stock", ascending=False),
    use_container_width=True
)

st.divider()

# =========================
# 📊 CHARTS
# =========================
g1, g2 = st.columns(2)

with g1:
    st.subheader("📈 מלאי לפי חברה")

    fig1 = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )

    st.plotly_chart(fig1, use_container_width=True)

with g2:
    st.subheader("🥧 סטטוס מלאי")

    fig2 = px.pie(
        filtered,
        names="סטטוס",
        values="stock"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 🧠 INSIGHT
# =========================
st.divider()

if len(filtered) > 0:
    top = filtered.sort_values("stock", ascending=False).iloc[0]

    st.success(f"⭐ מוצר מוביל: {top['SKU']} ({int(top['stock'])})")