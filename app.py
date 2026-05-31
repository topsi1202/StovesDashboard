import streamlit as st
import pandas as pd
import plotly.express as px

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

    st.title("📦 דשבורד מלאי כיריים")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "דגם",
            len(df)
        )

    with col2:
        st.metric(
            "",
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
        filtered = filtered[
            filtered["חברה"].isin(company)
        ]

    if stove_type:
        filtered = filtered[
            filtered["סוג"].isin(stove_type)
        ]

    if color:
        filtered = filtered[
            filtered["צבע"].isin(color)
        ]

    search = st.text_input(
        "חיפוש דגם"
    )

    if search:
        filtered = filtered[
            filtered["דגם"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    st.dataframe(
        filtered,
        use_container_width=True
    )

    chart = px.bar(
        filtered,
        x="חברה",
        y="מלאי"
    )

    st.plotly_chart(
        chart,
        use_container_width=True
    )