import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from backend.database.init_db import init_db
from frontend.pages.home_page import render_home

st.set_page_config(page_title="YKI Reading AI Coach", layout="wide")

st.markdown(
    """
<style>
:root {
    --yki-blue: #2563eb;
    --yki-blue-dark: #1d4ed8;
    --yki-blue-light: #eff6ff;
    --yki-border: #bfdbfe;
    --yki-text: #172554;
}

.stApp {
    color: var(--yki-text);
}

h1, h2, h3 {
    color: var(--yki-text);
}

a {
    color: var(--yki-blue);
}

div.stButton > button {
    border-color: var(--yki-blue);
    color: var(--yki-blue-dark);
    transition: background-color 120ms ease, color 120ms ease,
        border-color 120ms ease;
}

div.stButton > button:hover {
    border-color: var(--yki-blue-dark);
    color: var(--yki-blue-dark);
    background-color: var(--yki-blue-light);
}

div.stButton > button:focus-visible {
    outline: 2px solid var(--yki-blue);
    outline-offset: 2px;
}

input, textarea, [data-baseweb="select"] > div {
    border-color: var(--yki-border);
}

input:focus, textarea:focus {
    border-color: var(--yki-blue) !important;
    box-shadow: 0 0 0 1px var(--yki-blue) !important;
}

input[type="radio"], input[type="checkbox"] {
    accent-color: var(--yki-blue);
}

section[data-testid="stSidebar"] {
    background-color: var(--yki-blue-light);
}

div[data-testid="stExpander"] {
    border-color: var(--yki-border);
}

div[data-testid="stMetric"] {
    border: 1px solid var(--yki-border);
    border-radius: 0.75rem;
    background-color: #f8fbff;
    padding: 0.75rem;
}
</style>
""",
    unsafe_allow_html=True,
)

if not st.session_state.get("_database_initialized"):
    init_db()
    st.session_state["_database_initialized"] = True

render_home()
