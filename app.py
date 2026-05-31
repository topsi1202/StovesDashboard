import streamlit as st
import ui
import logic
import db

st.set_page_config(page_title="AI CONTROL NEXT", layout="wide")

db.init_db()

df = db.load_data()

ui.render_css()
ui.render_header()

if df.empty:
    st.warning("אין נתונים במערכת")
    st.stop()

df = logic.engine(df)

filtered = ui.filters(df)

ui.kpis(filtered)

ui.charts(filtered)

ui.table(filtered)

ui.insight(filtered)