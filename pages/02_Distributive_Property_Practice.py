import random
from typing import List, Tuple

import streamlit as st

try:
    from sympy import symbols, expand
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
    # Fallback flags to allow the page to render without import-time failures
    REPORTLAB_AVAILABLE = False
    def build_pdf(*args, **kwargs):
        raise RuntimeError("PDF builder unavailable. Open main page once or install requirements.")


VARS = ["a", "b", "x", "y", "m", "n"]


def rand_nonzero(lo: int, hi: int) -> int:
    while True:
        v = random.randint(lo, hi)
        if v != 0:
            return v


def one_problem(level: int) -> str:
    """Build one expression with roughly increasing difficulty by level 1..4.
    Level controls coefficient sizes, nesting, and variable variety.
    """
    # Variable pool grows with difficulty
    pool = VARS[: 2 + level]  # 3→ up to 'x', 4→ up to 'n'
    v1 = random.choice(pool)
    v2 = random.choice(pool)
    while v2 == v1 and level >= 3 and random.random() < 0.5:
        v2 = random.choice(pool)

    # Coefficient ranges by level
    coef_max = {1: 5, 2: 12, 3: 20, 4: 30}[level]
    def cpos(maxv=coef_max):
        return rand_nonzero(1, maxv)
    def cint(maxv=coef_max):
        # allow negatives as well
        z = random.randint(-maxv, maxv)
        return z if z != 0 else 1

    # Helper to mk linear term like "3a" or with explicit * when needed for clarity
    def lin(coeff: int, var: str) -> str:
        # Present nicely as 3a (no star) for worksheet readability
        sign = "-" if coeff < 0 else ""
        k = abs(coeff)
        return f"{sign}{k}{var}"

    # Assemble shapes by level
    if level == 1:
        # Basic: c ± k*(m v1 ± n)
        c = cint()
        k = cpos()
        m = cpos()
        n = random.randint(1, coef_max)
        inner_sign = random.choice(["+", "-"])
        outer_sign = random.choice(["+", "-"])
        expr = f"{c} {outer_sign} {k}*({lin(m, v1)} {inner_sign} {n})"
    elif level == 2:
        # Moderate: k*(m v1 ± n) ± c  OR  m2 v1 ± k*(m v1 ± n)
        c = cint()
        k = cpos()
        m = cpos()
        m2 = cpos()
        n = random.randint(1, coef_max)
        inner_sign = random.choice(["+", "-"])
        outer_sign = random.choice(["+", "-"])
        if random.random() < 0.5:
            expr = f"{k}*({lin(m, v1)} {inner_sign} {n}) {outer_sign} {c}"
        else:
            expr = f"{lin(m2, v1)} {outer_sign} {k}*({lin(m, v1)} {inner_sign} {n})"
    elif level == 3:
        # Harder: nested once k*(m v1 ± (p v2 ± n)) ± c
        c = cint()
        k = cpos()
        m = cpos()
        p = cpos()
        n = random.randint(1, coef_max)
        s1 = random.choice(["+", "-"])
        s2 = random.choice(["+", "-"])
        outer_sign = random.choice(["+", "-"])
        inner = f"{lin(m, v1)} {s1} ({lin(p, v2)} {s2} {n})"
        expr = f"{k}*({inner}) {outer_sign} {c}"
    else:
        # Level 4: longer, two distributive terms and/or deeper nesting
        # Example: k*(m v1 ± (p v2 ± n)) ± t*(q v1 ± r) ± c
        c = cint()
        k = cpos(); t = cpos()
        m = cpos(); p = cpos(); q = cpos(); r = random.randint(1, coef_max)
        s1 = random.choice(["+", "-"])
        s2 = random.choice(["+", "-"])
        s3 = random.choice(["+", "-"])
        s4 = random.choice(["+", "-"])
        left = f"{k}*({lin(m, v1)} {s1} ({lin(p, v2)} {s2} {r}))"
        right = f"{t}*({lin(q, v1)} {s3} {r})"
        expr = f"{left} {s4} {right} {random.choice(['+','-'])} {c}"

    # Normalize simple sign artifacts
    expr = (
        expr.replace("+-", "- ")
            .replace("- -", "+ ")
            .replace("- +", "- ")
            .replace("+ -", "- ")
    )
    return expr


def generate_distributive(n: int = 16) -> List[str]:
    """Return 16 expressions with difficulty in order: 7 easy, 7 medium, 2 hard.
    Mapping: easy -> level 1; medium -> alternate between levels 2 and 3; hard -> level 4.
    """
    exprs: List[str] = []
    count_easy = min(7, n)
    count_medium = min(7, max(0, n - count_easy))
    count_hard = max(0, n - count_easy - count_medium)

    # Easy (level 1)
    for _ in range(count_easy):
        exprs.append(one_problem(level=1))

    # Medium (levels 2/3 alternating)
    toggle = 2
    for _ in range(count_medium):
        exprs.append(one_problem(level=toggle))
        toggle = 3 if toggle == 2 else 2

    # Hard (level 4)
    for _ in range(count_hard):
        exprs.append(one_problem(level=4))

    return exprs


def try_expand(exprs: List[str]) -> List[str]:
    if not SYMPY_AVAILABLE:
        return ["" for _ in exprs]
    a, b, x, y, m, n = symbols("a b x y m n")
    locals_map = {"a": a, "b": b, "x": x, "y": y, "m": m, "n": n}
    transformations = standard_transformations + (implicit_multiplication_application,)
    answers: List[str] = []
    for e in exprs:
        try:
            # Allow implicit multiplication so strings like "3a" parse as 3*a
            s = parse_expr(e, local_dict=locals_map, transformations=transformations, evaluate=True)
            ans = expand(s)
            answers.append(str(ans))
        except Exception:
            answers.append("")
    return answers


def main():
    st.title("Distributive Property Practice (Algebra)")
    st.caption("Generates 8×2 expressions to practice correct order of operations and distribution.")

    col1, col2 = st.columns([1, 1])
    with col1:
        seed_text = st.text_input("Seed (optional)", value="")
    with col2:
        regen = st.button("Generate Set", type="primary")

    if seed_text.strip():
        random.seed(seed_text.strip())

    if "alg_problems" not in st.session_state or regen:
        st.session_state["alg_problems"] = generate_distributive(16)

    exprs = st.session_state["alg_problems"]

    st.subheader("Simplify the expressions below")
    left, right = st.columns(2)
    for i in range(8):
        with left:
            st.write(f"{i+1}) {exprs[i]} = ______")
        with right:
            st.write(f"{i+9}) {exprs[i + 8]} = ______")

    include_key = st.checkbox("Include Answer Key (requires sympy)", value=SYMPY_AVAILABLE)
    answers = try_expand(exprs) if include_key and SYMPY_AVAILABLE else ["" for _ in exprs]

    # Build a PDF using the shared builder (8x2 grid). Put blanks in a right column to avoid overflow.
    items: List[Tuple[str, str]] = [(e, a) for e, a in zip(exprs, answers)]

    if REPORTLAB_AVAILABLE:
        pdf_bytes = build_pdf(
            items,
            title="Distributive Property Practice — Simplify the expressions below",
            include_answer_key=bool(include_key and SYMPY_AVAILABLE),
            right_label="= ______",
            rows=8,
            cols=2,
        )
        st.download_button(
            label="Download Printable PDF",
            data=pdf_bytes,
            file_name="worksheet_distributive_8x2.pdf",
            mime="application/pdf",
        )
    else:
        st.info("PDF engine not available. Install reportlab on the system to enable PDF download.")


if __name__ == "__main__":
    main()
