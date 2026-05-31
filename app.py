st.markdown("""
<style>

/* ===== BACKGROUND (SOFT DARK, NOT BLACK) ===== */
.stApp {
    background: #0F172A;
    color: #E5E7EB;
    font-family: "Inter", sans-serif;
}

/* ===== TITLE (MODERN BLUE) ===== */
h1 {
    color: #60A5FA !important;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* ===== CARDS (SOFT GLASS LOOK) ===== */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px;
    backdrop-filter: blur(8px);
}

/* metric text */
[data-testid="metric-container"] label {
    color: #94A3B8 !important;
    font-size: 13px;
}

/* metric value */
[data-testid="metric-container"] div {
    color: #F8FAFC !important;
    font-weight: 700;
}

/* ===== SIDEBAR (CLEANER) ===== */
section[data-testid="stSidebar"] {
    background: #0B1220;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* ===== INPUTS ===== */
input {
    background: rgba(255,255,255,0.05) !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

/* ===== BUTTONS (MODERN BLUE) ===== */
.stButton > button {
    background: #60A5FA;
    color: #0B1220;
    font-weight: 700;
    border-radius: 10px;
    border: none;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #3B82F6;
}

/* ===== TABLE ===== */
div[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
}

/* ===== DIVIDER ===== */
hr {
    border: 1px solid rgba(255,255,255,0.06);
}

/* ===== TEXT ===== */
p, span, label {
    color: #CBD5E1;
}

</style>
""", unsafe_allow_html=True)