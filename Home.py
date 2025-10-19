import streamlit as st


st.set_page_config(
    page_title="Zhao learning center",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Zhao learning center")
st.write("Welcome! Choose a subject to get started.")

# Hide the sidebar (and its toggle) so only the main content shows
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { display: none !important; }
      [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Prefer native page links if available; otherwise fall back to a button
try:
    # Streamlit 1.22+ supports programmatic navigation; 1.27+ adds st.page_link
    st.page_link("pages/01_Math.py", label="Math")  # type: ignore[attr-defined]
    st.page_link("pages/05_English_Vocabulary.py", label="English Vocabulary")  # type: ignore[attr-defined]
except Exception:
    if st.button("Math", type="primary"):
        try:
            st.switch_page("pages/01_Math.py")  # type: ignore[attr-defined]
        except Exception:
            st.warning("Please use the sidebar to navigate to Math pages.")
    if st.button("English Vocabulary", type="primary"):
        try:
            st.switch_page("pages/05_English_Vocabulary.py")  # type: ignore[attr-defined]
        except Exception:
            st.warning("Please use the sidebar to navigate to English pages.")
