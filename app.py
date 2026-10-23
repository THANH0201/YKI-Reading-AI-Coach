import streamlit as st
from database.db import get_connection

st.title("YKI Reading AI Coach")

# Test database connection
try:
    conn = get_connection()
    st.success("Database Connected")
    conn.close()

except Exception as e:
    st.error(str(e))

# Article Input
article = st.text_area(
    "Paste Finnish Article",
    height=300
)

# Generate Exam Button
if st.button("Generate Exam"):
    
    if not article.strip():
        st.warning("Please paste an article first.")
    else:
        st.success("Article received!")
        st.write(article[:200] + "...")