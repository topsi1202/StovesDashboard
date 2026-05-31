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

    # ---------- ניקוי עמודות ----------
    df.columns = df.columns.str.strip()

    # ---------- המרה בטוחה של מלאי ----------
    df["מלאי"] = pd.to_numeric(df["מלאי"], errors="coerce").fillna(0)

    # ---------- קישור חיפוש גוגל ----------
    df["קישור חיפוש"] = df.apply(
        lambda row: "https://www.google.com/search?q=" +
        urllib.parse.quote(f"{row['חברה']} {row['דגם']}"),
        axis=1
    )

    st.title("📦 דשבורד מלאי כיריים")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "סה״כ פריטים",
            len(df)
        )

    with col2:
        st.metric(
            "סה״כ מלאי",
            int(df["מלאי"].sum())
        )

    company = st.sidebar.multiselect(
        "חברה",
        df["חברה"].unique()
    )

    stove_type = st.sidebar.multiselect(
        "סוג",
        df["סוג"].unique()
    )

    color = st.sidebar.multiselect(
        "צבע",
        df["צבע"].unique()
    )

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
            filtered["דגם"].astype(str).str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # ---------- טבלה עם לינק לחיץ ----------
    st.dataframe(
        filtered,
        column_config={
            "קישור חיפוש": st.column_config.LinkColumn("חיפוש בגוגל")
        },
        use_container_width=True
    )

    # ---------- גרף ----------
    chart = px.bar(
        filtered,
        x="חברה",
        y="מלאי"
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )