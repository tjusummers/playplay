import streamlit as st

st.set_page_config(
    page_title="English Vocabulary",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Hide the sidebar and style anchor links (for st.page_link)
st.markdown(
    """
    <style>
      [data-testid=\"stSidebar\"] { display: none !important; }
      [data-testid=\"collapsedControl\"] { display: none !important; }
      a { text-decoration: underline !important; font-weight: 700 !important; font-size: 1.05rem !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("English Vocabulary")
st.write("Choose a grade level (work in progress):")


def link_or_button(target_path: str, label: str):
    """Prefer separate page navigation; fall back to switch_page if needed."""
    try:
        st.page_link(target_path, label=label)  # type: ignore[attr-defined]
    except Exception:
        if st.button(label):
            try:
                st.switch_page(target_path)  # type: ignore[attr-defined]
            except Exception:
                st.warning(f"Open from the sidebar: {label}")


# Six grade-level links (separate pages)
link_or_button("pages/06_English_Kindergarten.py", "1) Kindergarten")
link_or_button("pages/07_English_First_Grade.py", "2) First Grade")
link_or_button("pages/08_English_Second_Grade.py", "3) Second Grade")
link_or_button("pages/09_English_Third_Grade.py", "4) Third Grade")
link_or_button("pages/10_English_Fourth_Grade.py", "5) Fourth Grade")
link_or_button("pages/11_English_Fifth_Grade.py", "6) Fifth Grade")


st.divider()
if st.button("Back to Home", type="primary", key="eng_back_home"):
    try:
        st.switch_page("Home.py")  # type: ignore[attr-defined]
    except Exception:
        st.warning("Use the Home page to navigate.")
