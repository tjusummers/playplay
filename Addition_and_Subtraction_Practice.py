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
    from reportlab.platypus import Paragraph, KeepInFrame, Table, TableStyle, SimpleDocTemplate, Spacer
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
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
        # Store problem string WITHOUT blanks; rendering will add blanks
        problems.append((f"{a} {op} {b}", answer))
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
    """Render problems to a printable PDF (rows x cols) using Platypus Table with wrapping.
    Uses KeepInFrame(shrink) to ensure content fits into fixed row heights across environments.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab not installed. Install with: pip install reportlab")

    buffer = io.BytesIO()

    # Page geometry
    width, height = letter
    margin = 0.6 * inch
    gutter = 0.5 * inch
    usable_width = width - 2 * margin
    col_width = (usable_width - gutter) / 2

    # Header reservation determines table row height
    reserved_header = 1.4 * inch  # space for title + name/date
    available_h = height - 2 * margin - reserved_header
    row_height = available_h / rows

    # Prepare data items to exactly rows*cols
    items = problems[: rows * cols]
    if len(items) < rows * cols:
        items += [("", 0)] * (rows * cols - len(items))

    # Styles
    base_font = 16
    name_style = ParagraphStyle(
        name="name",
        fontName="Helvetica",
        fontSize=11,
        leading=13,
    )
    title_style = ParagraphStyle(
        name="title",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_LEFT,
    )
    cell_style = ParagraphStyle(
        name="cell",
        fontName="Helvetica",
        fontSize=base_font,
        leading=base_font * 1.2,
        alignment=TA_LEFT,
    )

    def make_cell(text: str, max_w: float) -> KeepInFrame:
        p = Paragraph(text, cell_style)
        return KeepInFrame(max_w, row_height, [p], mode='shrink')

    # Build table data for first page
    data = []
    if right_label:
        q_w = max(36, col_width * right_label_ratio - 6)
        r_w = max(36, col_width - q_w)
        col_widths = [q_w, r_w, q_w, r_w]
        for r in range(rows):
            left_idx = r
            right_idx = r + rows
            left_text = items[left_idx][0]
            right_text = items[right_idx][0]
            left_para = make_cell(f"{left_idx + 1}) {left_text}", q_w)
            right_para = make_cell(f"{right_idx + 1}) {right_text}", q_w)
            data.append([left_para, Paragraph(right_label, cell_style), right_para, Paragraph(right_label, cell_style)])
    else:
        col_widths = [col_width, col_width]
        for r in range(rows):
            left_idx = r
            right_idx = r + rows
            left_text = items[left_idx][0]
            right_text = items[right_idx][0]
            left_para = make_cell(f"{left_idx + 1}) {left_text}", col_width)
            right_para = make_cell(f"{right_idx + 1}) {right_text}", col_width)
            data.append([left_para, right_para])

    # Construct story
    story: list = []
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
    )

    story.append(Paragraph(title, title_style))
    story.append(Paragraph("Name: __________________________  Date: _____________", name_style))
    story.append(Spacer(0, 0.2 * inch))

    tbl = Table(data, colWidths=col_widths, rowHeights=[row_height] * rows, repeatRows=0)
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        # Optionally draw light guides; commented out by default
        # ('GRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
    ]))
    story.append(tbl)

    # Answer Key page
    if include_answer_key:
        from reportlab.platypus import PageBreak
        story.append(PageBreak())
        story.append(Paragraph("Answer Key", title_style))
        story.append(Paragraph(title, name_style))
        story.append(Spacer(0, 0.2 * inch))

        ans_data = []
        for r in range(rows):
            left_idx = r
            right_idx = r + rows
            # Extract lhs without blanks for answers
            def lhs_text(t: str) -> str:
                return t.split('=')[0].strip() if '=' in t else t.strip()

            left_problem, left_ans = items[left_idx]
            right_problem, right_ans = items[right_idx]
            left_para = make_cell(f"{left_idx + 1}) {lhs_text(left_problem)} = {left_ans}", col_width)
            right_para = make_cell(f"{right_idx + 1}) {lhs_text(right_problem)} = {right_ans}", col_width)
            ans_data.append([left_para, right_para])

        ans_tbl = Table(ans_data, colWidths=[col_width, col_width], rowHeights=[row_height] * rows)
        ans_tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ans_tbl)

    # Build document
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def main():
    st.set_page_config(page_title="Addition and Subtraction Practice", page_icon="🧮", layout="centered")
    st.title("Addition and Subtraction Practice (3-digit) V6")
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
            st.write(f"{i+1}) {problems[i][0]} = ______")
        with right:
            st.write(f"{i+9}) {problems[i + 8][0]} = ______")

    # Build PDF and provide download
    try:
        pdf_bytes = build_pdf(problems, right_label="= ______")
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
