import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(
    page_title="OLYMPUS ENTERPRISE",
    layout="wide"
)

DB_NAME = "inventory.db"

# =========================
# 🗄️ DATABASE LAYER
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            model TEXT,
            type TEXT,
            color TEXT,
            stock REAL
        )
    """)

    conn.commit()
    conn.close()

def insert_data(df):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql("inventory", conn, if_exists="replace", index=False)
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM inventory", conn)
    conn.close()
    return df

init_db()

# =========================
# 📥 UPLOAD + INGEST
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

    for col in ["company", "model", "type", "color"]:
        df[col] = df[col].astype(str).str.strip()

    df["stock"] = pd.to_numeric(df["stock"], errors="coerce").fillna(0)

    insert_data(df)
    st.success("📡 הנתונים נטענו למסד הנתונים")

# =========================
# 📊 LOAD FROM DB
# =========================
df = load_data()

if df.empty:
    st.warning("אין נתונים עדיין – העלה קובץ Excel")
    st.stop()

# =========================
# 🧠 BUSINESS LAYER
# =========================
df["SKU"] = df["company"] + " " + df["model"]

def status(x):
    if x == 0:
        return "🔴 אזל"
    elif x <= 2:
        return "🟠 נמוך"
    return "🟢 תקין"

df["status"] = df["stock"].apply(status)

# =========================
# 📊 HEADER KPIs
# =========================
st.title("🚀 OLYMPUS ENTERPRISE MODE")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("פריטים", len(df))
col2.metric("סה״כ מלאי", int(df["stock"].sum()))
col3.metric("אזל", int((df["stock"] == 0).sum()))
col4.metric("נמוך", int((df["stock"] <= 2).sum()))
col5.metric("דגמים", df["model"].nunique())

st.divider()

# =========================
# 🔎 SEARCH ENGINE
# =========================
search = st.text_input("🔎 חיפוש ENTERPRISE")

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["SKU"].str.contains(search, case=False, na=False) |
        filtered["company"].str.contains(search, case=False, na=False) |
        filtered["model"].str.contains(search, case=False, na=False)
    ]

# =========================
# 🎛 FILTER ENGINE
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

st.divider()

# =========================
# ✏️ LIVE EDIT + WRITE BACK
# =========================
st.subheader("🧾 עריכה חיה (נשמר למסד נתונים)")

edited = st.data_editor(filtered, use_container_width=True, num_rows="dynamic")

if st.button("💾 שמור שינויים"):
    insert_data(edited)
    st.success("✔ הנתונים עודכנו במסד הנתונים")

st.divider()

# =========================
# 🚨 ALERTS
# =========================
low = filtered[filtered["stock"] <= 2]

if len(low) > 0:
    st.warning(f"⚠️ מלאי נמוך: {len(low)}")

# =========================
# 📊 ANALYTICS
# =========================
colg1, colg2 = st.columns(2)

with colg1:
    st.subheader("📈 מלאי לפי חברה")

    fig = px.bar(
        filtered.groupby("company")["stock"].sum().reset_index(),
        x="company",
        y="stock"
    )

    st.plotly_chart(fig, use_container_width=True)

with colg2:
    st.subheader("🥧 סטטוס מלאי")

    fig2 = px.pie(
        filtered,
        names="status",
        values="stock"
    )

    st.plotly_chart(fig2, use_container_width=True)

# =========================
# 🧠 INSIGHT ENGINE
# =========================
st.divider()

if len(filtered) > 0:
    top = filtered.sort_values("stock", ascending=False).iloc[0]

    st.success(f"👑 מוצר מוביל: {top['SKU']} ({int(top['stock'])})")