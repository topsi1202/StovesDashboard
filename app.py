import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

st.set_page_config(
    page_title="מלאי כיריים",
    layout="wide"
)

uploaded_file = st.file_uploader(
    "העלה קובץ מלאי",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(uploaded_file)

    # ---------- ניקוי בסיסי ----------
    df.columns = df.columns.str.strip()

    # ---------- המרות בטוחות ----------
    for col in ["חברה", "דגם", "סוג", "צבע"]:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("")

    if "מלאי" in df.columns:
        df["מלאי"] = pd.to_numeric(df["מלאי"], errors="coerce").fillna(0)
    else:
        df["מלאי"] = 0

    # ---------- יצירת שאילתא בטוחה ----------
    df["שאילתא"] = (
        df["חברה"].astype(str).fillna("") + " " +
        df["דגם"].astype(str).fillna("")
    )

    # ---------- לינקים ----------
    df["גוגל"] = df["שאילתא"].apply(
        lambda x: "https://www.google.com/search?q=" + urllib.parse.quote(x)
    )

    df["תמונה"] = df["שאילתא"].apply(
        lambda x: "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote(x)
    )

    df["KSP"] = df["שאילתא"].apply(
        lambda x: "https://ksp.co.il/web/search?q=" + urllib.parse.quote(x)
    )

    df["IVORY"] = df["שאילתא"].apply(
        lambda x: "https://www.ivory.co.il/catalog.php?act=cat&q=" + urllib.parse.quote(x)
    )

    df["ZAP"] = df["שאילתא"].apply(
        lambda x: "https://www.zap.co.il/search.aspx?keyword=" + urllib.parse.quote(x)
    )

    # ---------- כותרת ----------
    st.title("📦 דשבורד מלאי כיריים")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("סה״כ פריטים", len(df))

    with col2:
        st.metric("סה״כ מלאי", int(df["מלאי"].sum()))

    with col3:
        st.metric("דגמים", df["דגם"].nunique())

    # ---------- פילטרים ----------
    company = st.sidebar.multiselect("חברה", df["חברה"].unique())
    stove_type = st.sidebar.multiselect("סוג", df["סוג"].unique())
    color = st.sidebar.multiselect("צבע", df["צבע"].unique())

    filtered = df.copy()

    if company:
        filtered = filtered[filtered["חברה"].isin(company)]

    if stove_type:
        filtered = filtered[filtered["סוג"].isin(stove_type)]

    if color:
        filtered = filtered[filtered["צבע"].isin(color)]

    search = st.text_input("חיפוש דגם")

    if search:
        filtered = filtered[
            filtered["דגם"].str.contains(search, case=False, na=False)
        ]

    # ---------- טבלה ----------
    st.subheader("📊 נתוני מלאי עם קישורים")

    st.dataframe(
        filtered,
        column_config={
            "גוגל": st.column_config.LinkColumn("🔎 גוגל"),
            "תמונה": st.column_config.LinkColumn("🖼️ תמונה"),
            "KSP": st.column_config.LinkColumn("🛒 KSP"),
            "IVORY": st.column_config.LinkColumn("🛒 Ivory"),
            "ZAP": st.column_config.LinkColumn("🛒 Zap"),
        },
        use_container_width=True
    )

    # ---------- גרף ----------
    st.subheader("📈 מלאי לפי חברה")

    fig = px.bar(
        filtered,
        x="חברה",
        y="מלאי"
    )

    st.plotly_chart(fig, use_container_width=True)