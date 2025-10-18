import random
import re
from fractions import Fraction
from typing import List, Tuple

import streamlit as st

try:
    from sympy import symbols, Eq, solveset, S
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
    )
    SYMPY_AVAILABLE = True
except Exception:
    SYMPY_AVAILABLE = False

try:
    from Addition_and_Subtraction_Practice import build_pdf, REPORTLAB_AVAILABLE
except Exception:
    REPORTLAB_AVAILABLE = False
    def build_pdf(*args, **kwargs):
        raise RuntimeError("PDF builder unavailable. Open main page once or install requirements.")


def randint_nonzero(lo: int, hi: int) -> int:
    while True:
        v = random.randint(lo, hi)
        if v != 0:
            return v


def lhs_pattern_level1() -> str:
    # 2x + b  OR  (x - b)/d
    if random.random() < 0.5:
        a = randint_nonzero(1, 12)
        b = random.randint(-12, 12)
        return f"{a}x + {b}"
    else:
        b = random.randint(-12, 12)
        d = randint_nonzero(2, 9)
        return f"(x - {b})/{d}"


def lhs_pattern_level2() -> str:
    # a - (x/d + b)   OR  k*(x + b) - c
    if random.random() < 0.5:
        a = random.randint(-10, 10)
        d = randint_nonzero(2, 9)
        b = random.randint(1, 10)
        return f"{a} - (x/{d} + {b})"
    else:
        k = randint_nonzero(2, 9)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        return f"{k}*(x + {b}) - {c}"


def lhs_pattern_level3() -> str:
    # a*(x + b) - (x - c)/d   OR  a x + b - c x
    if random.random() < 0.5:
        a = randint_nonzero(2, 12)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        d = randint_nonzero(2, 9)
        return f"{a}*(x + {b}) - (x - {c})/{d}"
    else:
        a = randint_nonzero(1, 12)
        c = randint_nonzero(1, 12)
        b = random.randint(-12, 12)
        d = random.randint(-12, 12)
        return f"{a}x + {b} - {c}x - {d}"


def lhs_pattern_level4() -> str:
    # k*(x - a) + m*(x + b)/d   OR  (x - a)/d - (x + b)/t
    if random.random() < 0.5:
        k = randint_nonzero(2, 12)
        m = randint_nonzero(2, 12)
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        d = randint_nonzero(2, 9)
        return f"{k}*(x - {a}) + {m}*(x + {b})/{d}"
    else:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        d = randint_nonzero(2, 9)
        t = randint_nonzero(2, 9)
        return f"(x - {a})/{d} - (x + {b})/{t}"


def one_equation(level: int, solution: int) -> str:
    # Build a left-hand expression and set RHS to its value at x=solution.
    if level == 1:
        lhs = lhs_pattern_level1()
    elif level == 2:
        lhs = lhs_pattern_level2()
    elif level == 3:
        lhs = lhs_pattern_level3()
    else:
        lhs = lhs_pattern_level4()

    def to_eval_expr(s: str) -> str:
        # Insert explicit multiplication for terms like 3x -> 3*x
        s = re.sub(r"(?P<num>-?\d+)\s*x", r"\g<num>*x", s)
        return s

    def eval_at(xval: int) -> Fraction:
        expr = to_eval_expr(lhs)
        # Use Fraction to keep results exact
        local_dict = {"x": Fraction(xval)}
        return Fraction(eval(expr, {"__builtins__": {}}, local_dict))

    # Ensure expression actually depends on x (slope != 0)
    tries = 0
    while tries < 10:
        val = eval_at(solution)
        val2 = eval_at(solution + 1)
        if val != val2:
            break
        # Rebuild a new lhs if degenerate
        if level == 1:
            lhs = lhs_pattern_level1()
        elif level == 2:
            lhs = lhs_pattern_level2()
        elif level == 3:
            lhs = lhs_pattern_level3()
        else:
            lhs = lhs_pattern_level4()
        tries += 1

    rhs_val = eval_at(solution)
    rhs_str = f"{rhs_val.numerator}" if rhs_val.denominator == 1 else f"{rhs_val.numerator}/{rhs_val.denominator}"
    return f"{lhs} = {rhs_str}"


def generate_equations(n: int = 16) -> List[str]:
    """Return equations with difficulty in order: 7 easy, 7 medium, 2 hard.
    Mapping: easy -> level 1; medium -> alternate levels 2 and 3; hard -> level 4.
    Each equation has an integer solution |x| < 50.
    """
    eqs: List[str] = []
    count_easy = min(7, n)
    count_medium = min(7, max(0, n - count_easy))
    count_hard = max(0, n - count_easy - count_medium)

    # Easy
    for _ in range(count_easy):
        s = random.randint(-49, 49)
        eqs.append(one_equation(level=1, solution=s))

    # Medium alternating 2/3
    toggle = 2
    for _ in range(count_medium):
        s = random.randint(-49, 49)
        eqs.append(one_equation(level=toggle, solution=s))
        toggle = 3 if toggle == 2 else 2

    # Hard
    for _ in range(count_hard):
        s = random.randint(-49, 49)
        eqs.append(one_equation(level=4, solution=s))

    return [e.replace("+-", "- ").replace("- -", "+ ").replace("+ -", "- ") for e in eqs]


def solve_equations(eqs: List[str]) -> List[str]:
    if not SYMPY_AVAILABLE:
        return ["" for _ in eqs]
    x = symbols('x')
    transformations = standard_transformations + (implicit_multiplication_application,)
    ans: List[str] = []
    for e in eqs:
        try:
            left, right = e.split("=")
            L = parse_expr(left, transformations=transformations, evaluate=True)
            R = parse_expr(right, transformations=transformations, evaluate=True)
            sol = solveset(Eq(L, R), x, domain=S.Reals)
            # Present a single solution nicely, or set notation
            if sol.is_FiniteSet and len(sol) == 1:
                val = list(sol)[0]
                ans.append(f"x = {val}")
            else:
                ans.append(str(sol))
        except Exception:
            ans.append("")
    return ans


def main():
    # Hide sidebar on this page
    try:
        st.set_page_config(initial_sidebar_state="collapsed")
    except Exception:
        pass
    st.markdown(
        """
        <style>
          [data-testid=\"stSidebar\"] { display: none !important; }
          [data-testid=\"collapsedControl\"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Isolating a Variable - Solve the equations below")
    st.caption("Generates 8×2 linear equations in x with mixed difficulty and structure.")

    col1, col2 = st.columns([1, 1])
    with col1:
        seed_text = st.text_input("Seed (optional)", value="")
    with col2:
        regen = st.button("Generate Set", type="primary")

    

    if seed_text.strip():
        random.seed(seed_text.strip())

    if "solve_equations" not in st.session_state or regen:
        st.session_state["solve_equations"] = generate_equations(16)

    eqs = st.session_state["solve_equations"]

    # Preview 8 x 2 (numbered)
    st.subheader("Solve for x")
    left, right = st.columns(2)
    for i in range(8):
        with left:
            st.write(f"{i+1}) {eqs[i]}")
        with right:
            st.write(f"{i+9}) {eqs[i + 8]}")

    include_key = st.checkbox("Include Answer Key (requires sympy)", value=SYMPY_AVAILABLE)
    answers = solve_equations(eqs) if include_key and SYMPY_AVAILABLE else ["" for _ in eqs]

    # Prepare items for PDF (8x2). Pass equation only; no right-side blank.
    items: List[Tuple[str, str]] = [(eq, a.replace("x = ", "")) for eq, a in zip(eqs, answers)]

    if REPORTLAB_AVAILABLE:
        try:
            pdf_bytes = build_pdf(
            items,
            title="Isolating a Variable - Solve for x",
            include_answer_key=bool(include_key and SYMPY_AVAILABLE),
            rows=8,
            cols=2,
            answer_key_use_lhs=False, # force no LHS in key
            answer_key_prefix="", # and no prefix; shows only the value
            )
        except TypeError:
            # Fallback for older builder signature (won't crash; if you still see “lhs = value”,
            # restart Streamlit so the latest builder gets loaded)
            pdf_bytes = build_pdf(
            items,
            title="Isolating a Variable - Solve for x",
            include_answer_key=bool(include_key and SYMPY_AVAILABLE),
            rows=8,
            cols=2,
            )
        st.download_button(
            label="Download Printable PDF",
            data=pdf_bytes,
            file_name="worksheet_isolating_variable_8x2.pdf",
            mime="application/pdf",
        )
    else:
        st.info("PDF engine not available. Install reportlab to enable PDF download.")

    # Back to Math at bottom
    st.divider()
    if st.button("Back to Math", type="primary", key="back_to_math_isovar"):
        try:
            st.switch_page("pages/01_Math.py")  # type: ignore[attr-defined]
        except Exception:
            st.warning("Open the Math page from the sidebar.")


if __name__ == "__main__":
    main()
