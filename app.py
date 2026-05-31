import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="דשבורד מלאי כיריים",
    layout="wide"
)

# ---------- טעינה מהירה ----------
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\n", "")
    return df

uploaded_file = st.file_uploader(
    "העלה קובץ מלאי",
    type=["xlsx"]
)

if uploaded_file:

    df = load_data(uploaded_file)

    # ---------- ניקוי חכם ----------
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

    # ---------- KPI ----------
    st.title("📦 דשבורד מלאי כיריים")

    avg_stock = df["מלאי"].mean() if len(df) else 0

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("פריטים", len(df))
    col2.metric("סה״כ מלאי", int(df["מלאי"].sum()))
    col3.metric("ממוצע מלאי", round(avg_stock, 1))
    col4.metric("אזל מהמלאי", int((df["מלאי"] == 0).sum()))

    st.divider()

    # ---------- פילטרים ----------
    colf1, colf2, colf3 = st.columns(3)

    with colf1:
        company = st.multiselect("חברה", sorted(df["חברה"].unique()))

    with colf2:
        stove_type = st.multiselect("סוג", sorted(df["סוג"].unique()))

    with colf3:
        color = st.multiselect("צבע", sorted(df["צבע"].unique()))

    filtered = df.copy()

    if company:
        filtered = filtered[filtered["חברה"].isin(company)]

    if stove_type:
        filtered = filtered[filtered["סוג"].isin(stove_type)]

    if color:
        filtered = filtered[filtered["צבע"].isin(color)]

    # ---------- חיפוש ----------
    search = st.text_input("🔎 חיפוש (חברה / דגם)")

    if search:
        search = search.strip()
        filtered = filtered[
            filtered["חברה"].str.contains(search, case=False, na=False) |
            filtered["דגם"].str.contains(search, case=False, na=False)
        ]

    st.divider()

    # ---------- התראות ----------
    low_stock = filtered[filtered["מלאי"] <= 2]
    zero_stock = filtered[filtered["מלאי"] == 0]

    if len(low_stock) > 0:
        st.warning(f"⚠️ יש {len(low_stock)} מוצרים עם מלאי נמוך")

        st.dataframe(
            low_stock.sort_values("מלאי"),
            use_container_width=True
        )

    if len(zero_stock) > 0:
        st.error(f"❌ יש {len(zero_stock)} מוצרים שאזלו מהמלאי")

    # ---------- טבלה ----------
    st.subheader("📊 מלאי לפי דגמים")

    st.dataframe(
        filtered.sort_values("מלאי", ascending=False),
        use_container_width=True
    )

    st.divider()

    # ---------- גרפים מתקדמים ----------
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📈 טופ 10 חברות")

        top_company = filtered.groupby("חברה")["מלאי"].sum().reset_index()

        fig1 = px.bar(
            top_company.sort_values("מלאי", ascending=False).head(10),
            x="חברה",
            y="מלאי"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with colg2:
        st.subheader("🔥 טופ 10 דגמים")

        top_models = filtered.groupby("דגם")["מלאי"].sum().reset_index()

        fig2 = px.bar(
            top_models.sort_values("מלאי", ascending=False).head(10),
            x="דגם",
            y="מלאי"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # ---------- תובנה חכמה ----------
    st.divider()

    if len(filtered) > 0:
        top_item = filtered.sort_values("מלאי", ascending=False).iloc[0]

        st.success(
            f"🔥 מוצר מוביל: {top_item['חברה']} {top_item['דגם']} ({int(top_item['מלאי'])})"
        )