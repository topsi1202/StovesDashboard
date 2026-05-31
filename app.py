import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# =========================
# 🎨 עיצוב נקי ומודרני
# =========================
st.set_page_config(
    page_title="מערכת ניהול מלאי",
    layout="wide"
)

st.markdown("""
<style>
body {
    background-color: #F5F7FB;
    color: #111827;
}

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

h1, h2, h3 {
    color: #1F2937;
}

[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #E5E7EB;
    padding: 14px;
    border-radius: 12px;
    box-shadow: 0px 1px 3px rgba(0,0,0,0.05);
}

.stDataFrame {
    border-radius: 10px;
    overflow: hidden;
}

hr {
    margin: 1.5rem 0;
    border: none;
    border-top: 1px solid #E5E7EB;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🗄️ מסד נתונים
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
# 📥 טעינת קובץ
# =========================
uploaded_file = st.file_uploader("📦 העלה קובץ מלאי (Excel)", type=["xlsx"])

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
    st.success("✔ הנתונים נטענו למערכת")

# =========================
# 📊 טעינת מערכת
# =========================
df = load()

if df.empty:
    st.warning("אין נתונים במערכת – העלה קובץ")
    st.stop()

# =========================
# 🧠 לוגיקה עסקית
# =========================
df["SKU"] = df["company"] + " " + df["model"]

def status(x):
    if x == 0:
        return "🔴 אזל מהמלאי"
    elif x <= 2:
        return "🟠 מלאי נמוך"
    return "🟢 תקין"

df["סטטוס"] = df["stock"].apply(status)

# =========================
# 🏠 כותרת
# =========================
st.title("📊 מערכת ניהול מלאי כיריים")

st.markdown("---")

# =========================
# 📌 KPI
# =========================
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("סה״כ פריטים", len(df))
col2.metric("סה״כ מלאי", int(df["stock"].sum()))
col3.metric("אזל מהמלאי", int((df["stock"] == 0).sum()))
col4.metric("מלאי נמוך", int((df["stock"] <= 2).sum()))
col5.metric("מספר דגמים", df["model"].nunique())

st.markdown("---")

# =========================
# 🔎 חיפוש
# =========================
search = st.text_input("🔎 חיפוש לפי חברה / דגם")

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["SKU"].str.contains(search, case=False, na=False)
    ]

# =========================
# 🎛 פילטרים
# =========================
colf1, colf2, colf3 = st.columns(3)

with colf1:
    company = st.multiselect("חברה", sorted(filtered["company"].unique()))

with colf2:
    type_f = st.multiselect("סוג", sorted(filtered["type"].unique()))

with colf3:
    color = st.multiselect("צבע", sorted(filtered["color"].unique()))

if company:
    filtered = filtered[filtered["company"].isin(company)]

if type_f:
    filtered = filtered[filtered["type"].isin(type_f)]

if color:
    filtered = filtered[filtered["color"].isin(color)]

st.markdown("---")

# =========================
# 🚨 התראות
# =========================
low = filtered[filtered["stock"] <= 2]
zero = filtered[filtered["stock"] == 0]

if len(zero) > 0:
    st.error(f"❌ אזל מהמלאי: {len(zero)} מוצרים")

if len(low) > 0:
    st.warning(f"⚠️ מלאי נמוך: {len(low)} מוצרים")

# =========================
# 📋 טבלה
# =========================
st.subheader("📦 נתוני מלאי")

st.dataframe(
    filtered.sort_values("stock", ascending=False),
    use_container_width=True
)

st.markdown("---")

# =========================
# 📊 גרפים
# =========================
colg1, colg2 = st.columns(2)

with colg1:
    st.subheader("📈 מלאי לפי חברה")

    fig1 = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )

    st.plotly_chart(fig1, use_container_width=True)

with colg2:
    st.subheader("🥧 סטטוס מלאי")

    fig2 = px.pie(
        filtered,
        names="סטטוס",
        values="stock"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 🧠 תובנה
# =========================
st.markdown("---")

if len(filtered) > 0:
    top = filtered.sort_values("stock", ascending=False).iloc[0]

    st.success(f"⭐ מוצר מוביל: {top['SKU']} ({int(top['stock'])})")