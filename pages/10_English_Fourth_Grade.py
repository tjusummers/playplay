import streamlit as st

st.set_page_config(
    page_title="English Vocabulary — Fourth Grade",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      [data-testid=\"stSidebar\"] { display: none !important; }
      [data-testid=\"collapsedControl\"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Fourth Grade vocabulary")
st.write("Work in progress. Activities coming soon!")

st.divider()
if st.button("Back to English Vocabulary", type="primary"):
    try:
        st.switch_page("pages/05_English_Vocabulary.py")  # type: ignore[attr-defined]
    except Exception:
        st.warning("Use the Home → English Vocabulary link.")
