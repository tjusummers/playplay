import streamlit as st

st.set_page_config(
    page_title="Math",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("Math")
st.write("Choose a practice module:")

# Hide the sidebar and its toggle on the Math page
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { display: none !important; }
      [data-testid="collapsedControl"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)



# Style buttons to look like bold, underlined links
st.markdown(
    """
    <style>
      .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0.25rem 0 !important;
        color: inherit !important;
        text-decoration: underline !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        box-shadow: none !important;
      }
      .stButton > button:hover { opacity: 0.8; cursor: pointer; }
    </style>
    """,
    unsafe_allow_html=True,
)

def link_or_button(target_path: str, label: str):
    clicked = st.button(label)
    if clicked:
        try:
            st.switch_page(target_path)  # type: ignore[attr-defined]
        except Exception:
            st.warning(f"Open the page from the sidebar: {label}")


# Only three links as requested, numbered 1-3
link_or_button("pages/04_Addition_and_Subtraction_Practice_Page.py", "1) Addition and Subtraction")
link_or_button("pages/02_Distributive_Property_Practice.py", "2) Distributive Property Practice")
link_or_button("pages/03_Isolating_Variable_Practice.py", "3) Isolating Variable Practice")

# Back to Home button at the bottom
st.divider()

# Override style for the last button to appear as a blue primary button
st.markdown(
    """
    <style>
      .stButton:last-of-type > button {
        background-color: #1f6feb !important;
        color: #ffffff !important;
        border: 1px solid #1f6feb !important;
        border-radius: 4px !important;
        padding: 0.4rem 0.8rem !important;
        text-decoration: none !important;
        box-shadow: none !important;
      }
      .stButton:last-of-type > button:hover {
        filter: brightness(0.95);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button("Back to Home", key="back_home"):
    try:
        st.switch_page("Home.py")  # type: ignore[attr-defined]
    except Exception:
        st.warning("Use the sidebar or restart at Home.py")
