import platform
import sys
import streamlit as st


def pkg_ver(mod, attrs):
    for a in attrs:
        v = getattr(mod, a, None)
        if v:
            return str(v)
    return "unknown"


def main():
    st.title("Environment Info")
    st.caption("Compare these between local and Streamlit Cloud to ensure parity.")

    st.subheader("Python")
    st.code(sys.version)
    st.write("Executable:", sys.executable)
    st.write("Platform:", platform.platform())

    st.subheader("Packages")
    info = []
    try:
        import streamlit as _st
        info.append(("streamlit", pkg_ver(_st, ["__version__"])) )
    except Exception as e:
        info.append(("streamlit", f"error: {e}"))

    try:
        import reportlab as rl
        v = pkg_ver(rl, ["__version__", "Version"])
        info.append(("reportlab", v))
    except Exception as e:
        info.append(("reportlab", f"error: {e}"))

    try:
        import sympy as sp
        info.append(("sympy", pkg_ver(sp, ["__version__"])) )
    except Exception as e:
        info.append(("sympy", f"error: {e}"))

    try:
        import flask as fk
        info.append(("flask", pkg_ver(fk, ["__version__"])) )
    except Exception as e:
        info.append(("flask", f"error: {e}"))

    try:
        import pdfkit as pk
        info.append(("pdfkit", pkg_ver(pk, ["__version__"])) )
    except Exception as e:
        info.append(("pdfkit", f"error: {e}"))

    for name, ver in info:
        st.write(f"- {name}: {ver}")

    st.subheader("Next Steps")
    st.markdown(
        """
        - Open this page locally and on Streamlit Cloud; compare Python and package versions.
        - If they differ, pin the versions in `requirements.txt` and redeploy.
        - If Python versions differ, set the app's Python version in the cloud settings (or add a `runtime.txt` if supported) to match local.
        """
    )


if __name__ == "__main__":
    main()

