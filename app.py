st.markdown("""
<style>

/* ===== BASE BACKGROUND ===== */
.stApp {
    background: #0F172A; /* slate-900 אבל רך */
    color: #E2E8F0;
}

/* ===== TITLE ===== */
h1 {
    color: #38BDF8 !important; /* sky blue מודרני */
    font-weight: 800;
    letter-spacing: 0.5px;
}

/* ===== CARDS / METRICS ===== */
[data-testid="metric-container"] {
    background: #111C33;
    border: 1px solid #24324A;
    border-radius: 14px;
    padding: 14px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.25);
}

/* metric numbers */
[data-testid="metric-container"] label {
    color: #94A3B8 !important;
}
[data-testid="metric-container"] div {
    color: #F1F5F9 !important;
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: #0B1220;
    border-right: 1px solid #1E293B;
}

/* ===== INPUTS ===== */
input {
    background: #111C33 !important;
    color: #F8FAFC !important;
    border: 1px solid #24324A !important;
    border-radius: 10px !important;
}

/* ===== SELECT BOX ===== */
div[data-baseweb="select"] {
    background: #111C33 !important;
    border-radius: 10px;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #38BDF8, #0EA5E9);
    color: #0B1220;
    font-weight: 700;
    border-radius: 10px;
    border: none;
}

.stButton > button:hover {
    background: linear-gradient(90deg, #0EA5E9, #0284C7);
}

/* ===== TABLE ===== */
div[data-testid="stDataFrame"] {
    background: #0B1220;
    border: 1px solid #1E293B;
    border-radius: 12px;
}

/* ===== DIVIDER ===== */
hr {
    border: 1px solid #1E293B;
}

/* ===== TEXT CLEANUP ===== */
p, span {
    color: #CBD5E1;
}

</style>
""", unsafe_allow_html=True)