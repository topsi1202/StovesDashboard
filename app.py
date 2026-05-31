import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# =========================
# 🎨 GECKOBOARD STYLE UI
# =========================
st.set_page_config(
    page_title="Inventory Control Center",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #0F1226;
    color: #E5E7EB;
}

/* main app background */
.block-container {
    padding: 1.5rem 2rem;
}

/* KPI cards */
[data-testid="metric-container"] {
    background: #171A33;
    border: 1px solid #2A2F55;
    padding: 16px;
    border-radius: 14px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}

/* tables */
div[data-testid="stDataFrame"] {
    background-color: #171A33;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #2A2F55;
}

/* headers */
h1, h2, h3 {
    color: #E5E7EB;
}

/* sidebar */
section[data-testid="stSidebar"] {
    background-color: #11142A;
}

/* divider */
hr {
    border: 1px solid #2A2F55;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ DATABASE
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
# 📥 LOAD DATA
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
    st.warning("אין נתונים במערכת")
    st.stop()

# =========================
# 🧠 ENGINE
# =========================
df["SKU"] = df["company"] + " " + df["model"]

df["סטטוס"] = df["stock"].apply(
    lambda x: "🔴 אזל" if x == 0 else ("🟠 נמוך" if x <= 2 else "🟢 תקין")
)

# =========================
# 🏠 HEADER
# =========================
st.title("📊 מרכז בקרה למלאי – Inventory Control Center")

st.markdown("---")

# =========================
# 📌 KPI ROW (like dashboard cards)
# =========================
c1, c2, c3, c4 = st.columns(4)

c1.metric("סה״כ פריטים", len(df))
c2.metric("סה״כ מלאי", int(df["stock"].sum()))
c3.metric("אזל מהמלאי", int((df["stock"] == 0).sum()))
c4.metric("מלאי נמוך", int((df["stock"] <= 2).sum()))

st.markdown("---")

# =========================
# 🔎 SEARCH + FILTER PANEL
# =========================
col1, col2 = st.columns([1, 3])

with col1:
    search = st.text_input("🔎 חיפוש")

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

# =========================
# 🚨 ALERTS PANEL
# =========================
st.markdown("## ⚠ התראות מערכת")

a1, a2 = st.columns(2)

with a1:
    st.error(f"🔴 אזל מהמלאי: {(filtered['stock'] == 0).sum()}")

with a2:
    st.warning(f"🟠 מלאי נמוך: {(filtered['stock'] <= 2).sum()}")

st.markdown("---")

# =========================
# 📊 MAIN GRID (LIKE IMAGE)
# =========================
left, middle, right = st.columns([1.2, 1.2, 2.6])

# LEFT PANEL
with left:
    st.subheader("⏳ מלאי נמוך בזמן")

    low = filtered.sort_values("stock").head(10)
    st.dataframe(low, use_container_width=True)

# MIDDLE PANEL
with middle:
    st.subheader("📈 סטטוס מלאי")

    fig = px.pie(
        filtered,
        names="סטטוס",
        values="stock"
    )
    st.plotly_chart(fig, use_container_width=True)

# RIGHT PANEL
with right:
    st.subheader("📦 מלאי מלא לפי חברה")

    fig2 = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# =========================
# 📋 FULL TABLE (CONTROL CENTER)
# =========================
st.subheader("🧾 טבלת שליטה מרכזית")

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