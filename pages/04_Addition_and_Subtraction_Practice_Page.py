import streamlit as st

# Reuse the existing implementation without moving the file.
import Addition_and_Subtraction_Practice as add_sub


def _render():
    # Hide sidebar on this page
    st.set_page_config(initial_sidebar_state="collapsed")
    st.markdown(
        """
        <style>
          [data-testid=\"stSidebar\"] { display: none !important; }
          [data-testid=\"collapsedControl\"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Delegate to the existing app's main() to preserve all logic
    add_sub.main()

    # Back to Math at bottom
    st.divider()
    if st.button("Back to Math", type="primary", key="back_to_math_addsub"):
        try:
            st.switch_page("pages/01_Math.py")  # type: ignore[attr-defined]
        except Exception:
            st.warning("Open the Math page from the sidebar.")


if __name__ == "__main__":
    _render()
else:
    _render()
