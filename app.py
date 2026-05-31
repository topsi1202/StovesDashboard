import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OLYMPUS מלאי כיריים",
    layout="wide"
)

# ---------- טעינה ----------
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.replace("\n", "")
    return df

uploaded_file = st.file_uploader("העלה קובץ מלאי", type=["xlsx"])

if uploaded_file:

    df = load_data(uploaded_file)

    # ---------- ניקוי ----------
    for col in ["חברה", "דגם", "סוג", "צבע"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .fillna("")
            )

    if "מלאי" in df.columns:
        df["מלאי"] = pd.to_numeric(df["מלאי"], errors="coerce").fillna(0)
    else:
        df["מלאי"] = 0

    st.title("⚡ OLYMPUS – דשבורד מלאי מתקדם")

    # ---------- KPI ----------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("פריטים", len(df))
    col2.metric("סה״כ מלאי", int(df["מלאי"].sum()))
    col3.metric("אזל מהמלאי", int((df["מלאי"] == 0).sum()))
    col4.metric("מלאי נמוך", int((df["מלאי"] <= 2).sum()))

    st.divider()

    # ---------- חיפוש ----------
    search = st.text_input("🔎 חיפוש חכם (חברה / דגם)")

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["חברה"].str.contains(search, case=False, na=False) |
            filtered["דגם"].str.contains(search, case=False, na=False)
        ]

    # ---------- פילטרים ----------
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

    # ---------- התראות ----------
    low_stock = filtered[filtered["מלאי"] <= 2]

    if len(low_stock) > 0:
        st.warning(f"⚠️ {len(low_stock)} מוצרים עם מלאי נמוך")

    zero_stock = filtered[filtered["מלאי"] == 0]

    if len(zero_stock) > 0:
        st.error(f"❌ {len(zero_stock)} מוצרים אזלו מהמלאי")

    # ---------- עריכה בתוך הטבלה ----------
    st.subheader("🛠️ עריכת מלאי (בלייב)")

    edited_df = st.data_editor(
        filtered,
        num_rows="dynamic",
        use_container_width=True
    )

    # ---------- שמירה ----------
    if st.button("💾 שמור שינויים לקובץ Excel"):
        edited_df.to_excel("updated_inventory.xlsx", index=False)
        st.success("נשמר בהצלחה לקובץ updated_inventory.xlsx")

    st.divider()

    # ---------- גרפים ----------
    colg1, colg2 = st.columns(2)

    with colg1:
        st.subheader("📈 טופ חברות")

        fig1 = px.bar(
            filtered.groupby("חברה")["מלאי"].sum().reset_index(),
            x="חברה",
            y="מלאי"
        )

        st.plotly_chart(fig1, use_container_width=True)

    with colg2:
        st.subheader("🔥 טופ דגמים")

        fig2 = px.bar(
            filtered.groupby("דגם")["מלאי"].sum().reset_index(),
            x="דגם",
            y="מלאי"
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ---------- תובנה ----------
    if len(filtered) > 0:
        top = filtered.sort_values("מלאי", ascending=False).iloc[0]

        st.success(
            f"👑 מוצר מוביל: {top['חברה']} {top['דגם']} ({int(top['מלאי'])})"
        )