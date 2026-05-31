import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OLYMPUS ULTRA Inventory",
    layout="wide"
)

# =========================
# ⚡ LOAD + CACHE ENGINE
# =========================
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\n", "")
    return df

uploaded_file = st.file_uploader("📦 העלה קובץ מלאי", type=["xlsx"])

if uploaded_file:

    df = load_data(uploaded_file)

    # =========================
    # 🧼 DATA CLEANING ENGINE
    # =========================
    for col in ["חברה", "דגם", "סוג", "צבע"]:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .fillna("")
            )

    if "מלאי" not in df.columns:
        df["מלאי"] = 0
    else:
        df["מלאי"] = pd.to_numeric(df["מלאי"], errors="coerce").fillna(0)

    # =========================
    # 🧠 BUSINESS LAYER
    # =========================
    df["SKU"] = df["חברה"] + " " + df["דגם"]

    def status(x):
        if x == 0:
            return "🔴 אזל"
        elif x <= 2:
            return "🟠 נמוך"
        else:
            return "🟢 תקין"

    df["סטטוס"] = df["מלאי"].apply(status)

    # =========================
    # 📊 HEADER KPI
    # =========================
    st.title("🚀 OLYMPUS ULTRA – מערכת ניהול מלאי")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("פריטים", len(df))
    col2.metric("סה״כ מלאי", int(df["מלאי"].sum()))
    col3.metric("אזל", int((df["מלאי"] == 0).sum()))
    col4.metric("נמוך", int((df["מלאי"] <= 2).sum()))
    col5.metric("דגמים", df["דגם"].nunique())

    st.divider()

    # =========================
    # 🔎 SEARCH ENGINE
    # =========================
    search = st.text_input("🔎 חיפוש חכם (חברה / דגם / SKU)")

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["SKU"].str.contains(search, case=False, na=False) |
            filtered["חברה"].str.contains(search, case=False, na=False) |
            filtered["דגם"].str.contains(search, case=False, na=False)
        ]

    # =========================
    # 🎛 FILTER ENGINE
    # =========================
    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        company = st.multiselect("חברה", sorted(filtered["חברה"].unique()))

    with colf2:
        stove_type = st.multiselect("סוג", sorted(filtered["סוג"].unique()))

    with colf3:
        color = st.multiselect("צבע", sorted(filtered["צבע"].unique()))

    if company:
        filtered = filtered[filtered["חברה"].isin(company)]

    if stove_type:
        filtered = filtered[filtered["סוג"].isin(stove_type)]

    if color:
        filtered = filtered[filtered["צבע"].isin(color)]

    st.divider()

    # =========================
    # 🚨 ALERT SYSTEM
    # =========================
    low_stock = filtered[filtered["מלאי"] <= 2]
    zero_stock = filtered[filtered["מלאי"] == 0]

    if len(zero_stock) > 0:
        st.error(f"❌ אזל מהמלאי: {len(zero_stock)}")

    if len(low_stock) > 0:
        st.warning(f"⚠️ מלאי נמוך: {len(low_stock)}")

    # =========================
    # ✏️ EDITABLE ERP TABLE
    # =========================
    st.subheader("🧾 מערכת מלאי (עריכה חיה)")

    edited_df = st.data_editor(
        filtered.sort_values("מלאי", ascending=False),
        use_container_width=True,
        num_rows="dynamic"
    )

    # =========================
    # 💾 SAVE ENGINE
    # =========================
    if st.button("💾 שמור שינויים לקובץ"):
        edited_df.to_excel("inventory_updated.xlsx", index=False)
        st.success("נשמר בהצלחה: inventory_updated.xlsx")

    st.divider()

    # =========================
    # 📊 ANALYTICS ENGINE
    # =========================
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📈 מלאי לפי חברה")

        fig1 = px.bar(
            filtered.groupby("חברה")["מלאי"].sum().reset_index(),
            x="חברה",
            y="מלאי"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with colg2:
        st.subheader("🥧 סטטוס מלאי")

        fig2 = px.pie(
            filtered,
            names="סטטוס",
            values="מלאי"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # 🧠 INSIGHT ENGINE
    # =========================
    st.divider()

    if len(filtered) > 0:
        top = filtered.sort_values("מלאי", ascending=False).iloc[0]

        st.success(f"👑 מוצר מוביל: {top['SKU']} ({int(top['מלאי'])})")