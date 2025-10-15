import io
import random
from typing import List, Tuple

import streamlit as st

try:
    # ReportLab is commonly used for PDF creation
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    from reportlab.lib.utils import simpleSplit
    REPORTLAB_AVAILABLE = True
except Exception:  # pragma: no cover
    REPORTLAB_AVAILABLE = False


def generate_3digit_operands_addition() -> Tuple[int, int]:
    """Generate two 3-digit numbers a + b such that 100 <= a,b <= 999 and a+b <= 999.
    Strategy: choose a in [100, 899]; choose b in [100, 999-a].
    """
    a = random.randint(100, 899)
    b_max = 999 - a
    b = random.randint(100, b_max)
    return a, b


def generate_3digit_operands_subtraction() -> Tuple[int, int]:
    """Generate two 3-digit numbers a - b such that 100 <= a,b <= 999 and a-b >= 0."""
    a = random.randint(100, 999)
    b = random.randint(100, a)
    return a, b


def _carry_count_add(a: int, b: int) -> int:
    cnt = 0
    carry = 0
    for _ in range(3):
        da = a % 10
        db = b % 10
        if da + db + carry >= 10:
            cnt += 1
            carry = 1
        else:
            carry = 0
        a //= 10
        b //= 10
    return cnt


def _borrow_count_sub(a: int, b: int) -> int:
    # assumes a >= b and both 3-digit
    cnt = 0
    borrow = 0
    for _ in range(3):
        da = a % 10 - borrow
        db = b % 10
        if da < db:
            cnt += 1
            borrow = 1
        else:
            borrow = 0
        a //= 10
        b //= 10
    return cnt


def _gen_add_by_difficulty(tier: str) -> Tuple[int, int]:
    # tier in {"easy","medium","hard"}
    for _ in range(2000):
        a = random.randint(100, 899)
        b = random.randint(100, 999 - a)
        carries = _carry_count_add(a, b)
        if tier == "easy" and carries == 0:
            return a, b
        if tier == "medium" and carries == 1:
            return a, b
        if tier == "hard" and carries >= 2:
            return a, b
    # fallback any valid
    return generate_3digit_operands_addition()


def _gen_sub_by_difficulty(tier: str) -> Tuple[int, int]:
    for _ in range(2000):
        a = random.randint(100, 999)
        b = random.randint(100, a)
        borrows = _borrow_count_sub(a, b)
        if tier == "easy" and borrows == 0:
            return a, b
        if tier == "medium" and borrows == 1:
            return a, b
        if tier == "hard" and borrows >= 2:
            return a, b
    return generate_3digit_operands_subtraction()


def generate_problems(n: int = 16) -> List[Tuple[str, int]]:
    """Generate n mixed addition/subtraction problems with increasing difficulty.

    Difficulty distribution for n=16: 7 easy, 7 medium, 2 hard in order.
    Returns list of (problem_str, answer).
    """
    tiers = []
    if n >= 16:
        tiers = ["easy"] * 7 + ["medium"] * 7 + ["hard"] * 2
    else:
        # proportionally scale for other n values
        e = max(0, round(n * 7 / 16))
        m = max(0, round(n * 7 / 16))
        h = max(0, n - e - m)
        tiers = ["easy"] * e + ["medium"] * m + ["hard"] * h

    problems: List[Tuple[str, int]] = []
    for tier in tiers:
        op = random.choice(['+', '-'])
        if op == '+':
            a, b = _gen_add_by_difficulty(tier)
            answer = a + b
        else:
            a, b = _gen_sub_by_difficulty(tier)
            answer = a - b
        problems.append((f"{a} {op} {b} = ______", answer))
    return problems


def build_pdf(
    problems: List[Tuple[str, int]],
    title: str = "Addition & Subtraction Practice",
    include_answer_key: bool = True,
    right_label: str | None = None,
    right_label_ratio: float = 0.62,
    rows: int = 8,
    cols: int = 2,
) -> bytes:
    """Render problems to a printable PDF (rows x cols). Returns PDF bytes.
    Requires reportlab. If not available, raises RuntimeError with install hint.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError(
            "ReportLab not installed. Install with: pip install reportlab"
        )

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Page layout
    margin = 0.6 * inch
    top_margin = 0.9 * inch
    gutter = 0.5 * inch
    usable_width = width - 2 * margin
    col_width = (usable_width - gutter) / 2

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - top_margin + 0.35 * inch, title)

    # Sub-title / name line
    c.setFont("Helvetica", 11)
    c.drawString(margin, height - top_margin, "Name: __________________________  Date: _____________")

    # Grid settings: default 8 rows x 2 columns
    start_y = height - top_margin - 0.4 * inch
    row_height = (height - (2 * margin) - top_margin) / (rows + 0.5)  # comfortable spacing
    base_font_size = 16
    c.setFont("Helvetica", base_font_size)

    # Ensure we have exactly rows*cols problems
    items = problems[: rows * cols]
    if len(items) < rows * cols:
        items += [("", 0)] * (rows * cols - len(items))

    def draw_wrapped_fit(text: str, x: float, y: float, max_width: float):
        """Draw text wrapped, reducing font size if needed to fit row height."""
        min_font = 10
        fs = base_font_size
        while fs >= min_font:
            lines = simpleSplit(text, "Helvetica", fs, max_width)
            line_height = fs * 1.2
            total_height = len(lines) * line_height
            if total_height <= row_height or fs == min_font:
                c.setFont("Helvetica", fs)
                for i, line in enumerate(lines):
                    c.drawString(x, y - i * line_height, line)
                # restore base font for subsequent calls
                c.setFont("Helvetica", base_font_size)
                return
            fs -= 1

    for r in range(rows):
        y = start_y - r * row_height
        for col in range(cols):
            idx = r + col * rows
            text = items[idx][0]
            x = margin + col * (col_width + gutter)
            prefix = f"{idx + 1}) " if text else ""
            if right_label:
                # Draw question and a separate right-side label (e.g., "x = ______") for spacing
                rx = x + col_width * right_label_ratio
                draw_wrapped_fit(prefix + text, x, y, max_width=(rx - x - 6))
                c.setFont("Helvetica", base_font_size)
                c.drawString(rx, y, right_label)
            else:
                draw_wrapped_fit(prefix + text, x, y, max_width=col_width)

    if include_answer_key:
        # Go to second page: Answer Key
        c.showPage()

        # Answer key title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - top_margin + 0.35 * inch, "Answer Key")
        c.setFont("Helvetica", 11)
        c.drawString(margin, height - top_margin, title)

        # Answers in same grid
        c.setFont("Helvetica", base_font_size)
        for r in range(rows):
            y = start_y - r * row_height
            for col in range(cols):
                idx = r + col * rows
                if idx >= len(items):
                    continue
                problem_text, ans = items[idx]
                if not problem_text:
                    continue
                # Extract the left-hand expression before blanks if present
                if "______" in problem_text or " = " in problem_text:
                    lhs = problem_text.split("=")[0].strip()
                else:
                    lhs = problem_text.strip()
                numbered = f"{idx + 1}) {lhs} = {ans}"
                x = margin + col * (col_width + gutter)
                # Wrap answer lines too in case of long symbolic answers; shrink if necessary
                draw_wrapped_fit(numbered, x, y, max_width=col_width)

        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def main():
    st.set_page_config(page_title="Addition and Subtraction Practice", page_icon="🧮", layout="centered")
    st.title("Addition and Subtraction Practice (3-digit)")
    st.caption("Generates 8×2 mixed addition and subtraction with results between 0 and 999.")

    # Controls
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        seed_text = st.text_input("Seed (optional)", value="")
    with col2:
        regen = st.button("Generate Worksheet", type="primary")

    if seed_text.strip():
        try:
            random.seed(int(seed_text.strip()))
        except ValueError:
            random.seed(seed_text.strip())  # allow any string as seed

    # Persist problems in session state
    if "problems" not in st.session_state or regen:
        st.session_state["problems"] = generate_problems(16)

    problems = st.session_state["problems"]

    # Preview on page: 8 rows x 2 columns (numbered)
    st.subheader("Preview")
    left, right = st.columns(2)
    for i in range(8):
        with left:
            st.write(f"{i+1}) {problems[i][0]}")
        with right:
            st.write(f"{i+9}) {problems[i + 8][0]}")

    # Build PDF and provide download
    try:
        pdf_bytes = build_pdf(problems)
        st.download_button(
            label="Download Printable PDF",
            data=pdf_bytes,
            file_name="worksheet_3digit_add_sub_8x2.pdf",
            mime="application/pdf",
        )
    except RuntimeError as e:
        st.warning(str(e))
        st.info("If you do not want to install ReportLab, I can also export a plain text file.")
        txt = "\n".join([p[0] for p in problems])
        st.download_button(
            label="Download as .txt (fallback)",
            data=txt,
            file_name="worksheet_3digit_add_sub_10x2.txt",
            mime="text/plain",
        )


if __name__ == "__main__":
    main()
