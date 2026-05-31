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

    # ---------- ניקוי בסיסי ----------
    df.columns = df.columns.str.strip()

    # ניקוי טקסט עמוק (רווחים כפולים וכו')
    for col in ["חברה", "דגם", "סוג", "צבע"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .fillna("")
            )

    # ---------- מלאי ----------
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
    col3.metric("מלאי נמוך", len(df[df["מלאי"] <= 2]))
    col4.metric("אזל מהמלאי", len(df[df["מלאי"] == 0]))

    st.divider()

    # ---------- פילטרים ----------
    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        company = st.multiselect(
            "חברה",
            sorted(df["חברה"].dropna().unique())
        )

    with colf2:
        stove_type = st.multiselect(
            "סוג",
            sorted(df["סוג"].dropna().unique())
        )

    with colf3:
        color = st.multiselect(
            "צבע",
            sorted(df["צבע"].dropna().unique())
        )

    filtered = df.copy()

    if company:
        filtered = filtered[filtered["חברה"].isin(company)]

    if stove_type:
        filtered = filtered[filtered["סוג"].isin(stove_type)]

    if color:
        filtered = filtered[filtered["צבע"].isin(color)]

    # ---------- חיפוש חכם ----------
    search = st.text_input("🔎 חיפוש (חברה / דגם)")

    if search:
        search = search.strip()
        filtered = filtered[
            filtered["חברה"].str.contains(search, case=False, na=False) |
            filtered["דגם"].str.contains(search, case=False, na=False)
        ]

    st.divider()

    # ---------- התראה ----------
    low_stock = filtered[filtered["מלאי"] <= 2]

    if not low_stock.empty:
        st.warning("⚠️ יש מוצרים עם מלאי נמוך")

        st.dataframe(
            low_stock[["חברה", "דגם", "מלאי"]],
            use_container_width=True
        )

    # ---------- טבלה ----------
    st.subheader("📊 נתוני מלאי")

    styled = filtered.copy()

    st.dataframe(
        styled.sort_values("מלאי", ascending=False),
        use_container_width=True
    )

    st.divider()

    # ---------- גרפים ----------
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📈 מלאי לפי חברה")

        fig1 = px.bar(
            filtered,
            x="חברה",
            y="מלאי"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with colg2:
        st.subheader("🥧 התפלגות סוגים")

        fig2 = px.pie(
            filtered,
            names="סוג",
            values="מלאי"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ---------- תובנה חכמה ----------
    st.divider()

    top_item = filtered.sort_values("מלאי", ascending=False).head(1)

    if not top_item.empty:
        st.success(
            f"🔥 מוצר מוביל במלאי: {top_item.iloc[0]['חברה']} {top_item.iloc[0]['דגם']} ({int(top_item.iloc[0]['מלאי'])})"
        )