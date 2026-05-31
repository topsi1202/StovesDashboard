import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="דשבורד מלאי כיריים",
    layout="wide"
)

uploaded_file = st.file_uploader(
    "העלה קובץ מלאי",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # ---------- ניקוי שמות עמודות ----------
    df.columns = df.columns.str.strip()

    # ---------- ניקוי טקסט בכל השדות החשובים ----------
    for col in ["חברה", "דגם", "סוג", "צבע"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().fillna("")

    # ---------- תיקון מלאי ----------
    if "מלאי" in df.columns:
        df["מלאי"] = pd.to_numeric(df["מלאי"], errors="coerce").fillna(0)
    else:
        df["מלאי"] = 0

    # ---------- שאילתא ----------
    df["שאילתא"] = df["חברה"] + " " + df["דגם"]

    # ---------- KPIs ----------
    st.title("📦 דשבורד מלאי כיריים")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("סה״כ פריטים", len(df))
    col2.metric("סה״כ מלאי", int(df["מלאי"].sum()))
    col3.metric("מלאי נמוך (≤2)", len(df[df["מלאי"] <= 2]))
    col4.metric("אזל מהמלאי", len(df[df["מלאי"] == 0]))

    st.divider()

    # ---------- פילטרים (עם ניקוי כפילויות) ----------
    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        company = st.multiselect("חברה", sorted(df["חברה"].dropna().unique()))

    with colf2:
        stove_type = st.multiselect(
            "סוג",
            sorted(df["סוג"].dropna().str.strip().unique())
        )

    with colf3:
        color = st.multiselect("צבע", sorted(df["צבע"].dropna().unique()))

    filtered = df.copy()

    if company:
        filtered = filtered[filtered["חברה"].isin(company)]

    if stove_type:
        filtered = filtered[filtered["סוג"].isin(stove_type)]

    if color:
        filtered = filtered[filtered["צבע"].isin(color)]

    # ---------- חיפוש ----------
    search = st.text_input("🔎 חיפוש דגם / חברה")

    if search:
        filtered = filtered[
            filtered["דגם"].str.contains(search, case=False, na=False) |
            filtered["חברה"].str.contains(search, case=False, na=False)
        ]

    st.divider()

    # ---------- התראה ----------
    low_df = filtered[filtered["מלאי"] <= 2]

    if not low_df.empty:
        st.warning("⚠️ מלאי נמוך קיים במערכת")
        st.dataframe(low_df[["חברה", "דגם", "מלאי"]], use_container_width=True)

    # ---------- טבלה ----------
    st.subheader("📊 נתוני מלאי")

    st.dataframe(filtered, use_container_width=True)

    st.divider()

    # ---------- גרפים ----------
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📈 מלאי לפי חברה")

        fig = px.bar(
            filtered,
            x="חברה",
            y="מלאי"
        )

        st.plotly_chart(fig, use_container_width=True)

    with colg2:
        st.subheader("🥧 סוגים")

        fig2 = px.pie(
            filtered,
            names="סוג",
            values="מלאי"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ---------- תובנה ----------
    st.divider()

    top = filtered.sort_values("מלאי", ascending=False).head(1)

    if not top.empty:
        st.success(
            f"🔥 הכי הרבה מלאי: {top.iloc[0]['חברה']} {top.iloc[0]['דגם']} ({int(top.iloc[0]['מלאי'])})"
        )