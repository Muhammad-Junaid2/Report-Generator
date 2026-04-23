"""
PDF Report Generator — core generation logic using ReportLab.
Supports Student and Company (Employee) report types.
"""
import os
import sys
from datetime import datetime
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, PageBreak, KeepTogether,
)
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
from reportlab.lib.colors import HexColor

from src.models import StudentRecord, EmployeeRecord

# ─────────────────── COLOUR PALETTE ────────────────────
STUDENT_PRIMARY   = HexColor("#0D47A1")
STUDENT_ACCENT    = HexColor("#1565C0")
STUDENT_LIGHT     = HexColor("#E3F2FD")
STUDENT_DARK      = HexColor("#0A2E6E")

COMPANY_PRIMARY   = HexColor("#1B5E20")
COMPANY_ACCENT    = HexColor("#2E7D32")
COMPANY_LIGHT     = HexColor("#E8F5E9")
COMPANY_DARK      = HexColor("#0A3D0F")

PASS_COLOR  = HexColor("#1B5E20")
FAIL_COLOR  = HexColor("#B71C1C")
GOLD        = HexColor("#F57F17")
GRAY_LIGHT  = HexColor("#F5F5F5")
GRAY_MID    = HexColor("#9E9E9E")
TEXT_DARK   = HexColor("#212121")


# ─────────────────── STYLES FACTORY ─────────────────────
def _build_styles(primary, accent, dark):
    base = getSampleStyleSheet()

    styles = {
        "ReportTitle": ParagraphStyle(
            "ReportTitle", fontSize=22, fontName="Helvetica-Bold",
            textColor=colors.white, alignment=TA_CENTER, spaceAfter=2,
        ),
        "ReportSubtitle": ParagraphStyle(
            "ReportSubtitle", fontSize=11, fontName="Helvetica",
            textColor=HexColor("#BBDEFB"), alignment=TA_CENTER, spaceAfter=0,
        ),
        "SectionHeader": ParagraphStyle(
            "SectionHeader", fontSize=13, fontName="Helvetica-Bold",
            textColor=primary, spaceBefore=10, spaceAfter=4,
            borderPad=4,
        ),
        "BodyText": ParagraphStyle(
            "BodyText", fontSize=9, fontName="Helvetica",
            textColor=TEXT_DARK, leading=14,
        ),
        "SmallLabel": ParagraphStyle(
            "SmallLabel", fontSize=8, fontName="Helvetica",
            textColor=GRAY_MID,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader", fontSize=8, fontName="Helvetica-Bold",
            textColor=colors.white, alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell", fontSize=8, fontName="Helvetica",
            textColor=TEXT_DARK, alignment=TA_CENTER,
        ),
        "MetaValue": ParagraphStyle(
            "MetaValue", fontSize=10, fontName="Helvetica-Bold",
            textColor=primary,
        ),
        "MetaLabel": ParagraphStyle(
            "MetaLabel", fontSize=8, fontName="Helvetica",
            textColor=GRAY_MID,
        ),
        "Footer": ParagraphStyle(
            "Footer", fontSize=7, fontName="Helvetica",
            textColor=GRAY_MID, alignment=TA_CENTER,
        ),
        "Highlight": ParagraphStyle(
            "Highlight", fontSize=10, fontName="Helvetica-Bold",
            textColor=primary, alignment=TA_CENTER,
        ),
    }
    return styles


# ─────────────────── HELPER FLOWABLES ───────────────────
def _divider(color, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4, spaceBefore=4)


def _section_heading(text, styles, accent):
    return KeepTogether([
        _divider(accent),
        Paragraph(f"● {text}", styles["SectionHeader"]),
    ])


def _kpi_table(kpi_pairs, primary, accent, light, width):
    """Build a row of KPI boxes."""
    col_w = width / len(kpi_pairs)
    data = [[Paragraph(v, ParagraphStyle("kv", fontSize=15, fontName="Helvetica-Bold",
                                          textColor=primary, alignment=TA_CENTER)),
              Paragraph(l, ParagraphStyle("kl", fontSize=8, fontName="Helvetica",
                                          textColor=GRAY_MID, alignment=TA_CENTER))]
             for v, l in kpi_pairs]
    # Transpose: two rows (value row, label row)
    val_row   = [d[0] for d in data]
    label_row = [d[1] for d in data]
    t = Table([val_row, label_row], colWidths=[col_w] * len(kpi_pairs))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), light),
        ("BOX",        (0, 0), (-1, -1), 0.5, accent),
        ("LINEAFTER",  (0, 0), (-2, -1), 0.3, accent),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


# ─────────────────── STUDENT PDF ────────────────────────
def generate_student_report(
    records: List[StudentRecord],
    output_path: str,
    institution: str = "National University of Technology",
    semester: str = "Fall 2024",
    logo_path: Optional[str] = None,
    chart_paths: Optional[dict] = None,
    password: Optional[str] = None,
):
    primary, accent, light, dark = STUDENT_PRIMARY, STUDENT_ACCENT, STUDENT_LIGHT, STUDENT_DARK
    styles = _build_styles(primary, accent, dark)
    W, H = A4
    margin = 1.8 * cm
    content_w = W - 2 * margin

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
        title=f"{institution} — Student Report",
        author="ReportGen Pro",
    )

    story = []
    now = datetime.now()

    # ── HEADER BANNER ──
    banner_rows = []
    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=4*cm, height=1.1*cm)
        banner_rows.append(logo_img)

    banner_rows += [
        Spacer(1, 0.3*cm),
        Paragraph(institution, styles["ReportTitle"]),
        Paragraph(f"Student Academic Performance Report — {semester}", styles["ReportSubtitle"]),
        Spacer(1, 0.3*cm),
        Paragraph(f"Generated: {now.strftime('%A, %d %B %Y at %I:%M %p')}", ParagraphStyle(
            "gen", fontSize=8, fontName="Helvetica", textColor=HexColor("#90CAF9"), alignment=TA_CENTER)),
    ]

    banner_table = Table([[col] for col in banner_rows], colWidths=[content_w])
    banner_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), primary),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 0.5*cm))

    # ── KPI SUMMARY ──
    if records:
        avg_all    = round(sum(r.average for r in records) / len(records), 1)
        pass_count = sum(1 for r in records if r.status == "Pass")
        avg_attend = round(sum(r.attendance for r in records) / len(records), 1)
        top        = max(records, key=lambda r: r.average)
        kpis = [
            (str(len(records)), "Total Students"),
            (str(avg_all), "Class Average"),
            (f"{pass_count}/{len(records)}", "Passed"),
            (f"{avg_attend}%", "Avg Attendance"),
            (top.name.split()[0], "Top Performer"),
        ]
        story.append(_kpi_table(kpis, primary, accent, light, content_w))
        story.append(Spacer(1, 0.5*cm))

    # ── MAIN DATA TABLE ──
    story.append(_section_heading("Detailed Student Results", styles, accent))
    story.append(Spacer(1, 0.2*cm))

    col_headers = ["ID", "Name", "Math", "Sci", "Eng", "Hist", "CS", "Attend", "Avg", "Grade", "Result"]
    col_widths   = [1.5*cm, 4*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.2*cm, 1.4*cm, 1.4*cm, 1.4*cm, 1.5*cm]

    header_row = [Paragraph(h, styles["TableHeader"]) for h in col_headers]
    data_rows  = []
    for i, r in enumerate(records):
        row_data = r.to_table_row()
        result_para = Paragraph(
            row_data[-1],
            ParagraphStyle("res", fontSize=8, fontName="Helvetica-Bold",
                           textColor=PASS_COLOR if row_data[-1] == "Pass" else FAIL_COLOR,
                           alignment=TA_CENTER)
        )
        row = [Paragraph(cell, styles["TableCell"]) for cell in row_data[:-1]] + [result_para]
        data_rows.append(row)

    table = Table([header_row] + data_rows, colWidths=col_widths, repeatRows=1)
    row_style = []
    for i in range(1, len(data_rows) + 1):
        bg = GRAY_LIGHT if i % 2 == 0 else colors.white
        row_style.append(("BACKGROUND", (0, i), (-1, i), bg))

    table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), primary),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUND", (0, 1), (-1, -1), [colors.white, GRAY_LIGHT]),
        ("GRID",          (0, 0), (-1, -1), 0.3, HexColor("#BDBDBD")),
        ("BOX",           (0, 0), (-1, -1), 0.8, accent),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        *row_style,
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    # ── CHARTS PAGE ──
    if chart_paths:
        story.append(PageBreak())
        story.append(_section_heading("Analytics & Visual Insights", styles, accent))
        story.append(Spacer(1, 0.3*cm))

        chart_items = []
        for label, key in [("Grade Distribution", "grade_pie"),
                            ("Performance Overview", "avg_bar"),
                            ("Subject Averages (Radar)", "radar")]:
            p = chart_paths.get(key)
            if p and os.path.exists(p):
                chart_items.append((label, p))

        # Place charts 2-per-row
        for i in range(0, len(chart_items), 2):
            row_charts = chart_items[i:i+2]
            cells = []
            for label, path in row_charts:
                img = Image(path, width=8.5*cm, height=6.5*cm)
                caption = Paragraph(label, ParagraphStyle("cap", fontSize=8, fontName="Helvetica",
                                                           textColor=GRAY_MID, alignment=TA_CENTER))
                cells.append([img, caption])

            if len(cells) == 1:
                cells.append(["", ""])

            chart_table = Table(
                [[cells[0][0], cells[1][0]], [cells[0][1], cells[1][1]]],
                colWidths=[content_w / 2, content_w / 2],
            )
            chart_table.setStyle(TableStyle([
                ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(chart_table)
            story.append(Spacer(1, 0.3*cm))

        # Full-width chart
        for label, key in [("Detailed Performance Bar", "avg_bar")]:
            p = chart_paths.get(key)
            if p and os.path.exists(p):
                img = Image(p, width=content_w * 0.85, height=6*cm)
                story.append(img)

    # ── FOOTER ──
    story.append(Spacer(1, 0.5*cm))
    story.append(_divider(accent))
    story.append(Paragraph(
        f"© {now.year} {institution}  |  ReportGen Pro  |  Confidential Academic Document  |  Page Generated: {now.strftime('%d-%m-%Y %H:%M')}",
        styles["Footer"]
    ))

    doc.build(story)

    # Password protect if requested
    if password:
        _encrypt_pdf(output_path, password)

    return output_path


# ─────────────────── COMPANY PDF ────────────────────────
def generate_company_report(
    records: List[EmployeeRecord],
    output_path: str,
    company_name: str = "TechCorp International",
    period: str = "Q4 2024",
    logo_path: Optional[str] = None,
    chart_paths: Optional[dict] = None,
    password: Optional[str] = None,
):
    primary, accent, light, dark = COMPANY_PRIMARY, COMPANY_ACCENT, COMPANY_LIGHT, COMPANY_DARK
    styles = _build_styles(primary, accent, dark)
    W, H = A4
    margin = 1.8 * cm
    content_w = W - 2 * margin

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
        title=f"{company_name} — Employee Report",
        author="ReportGen Pro",
    )

    story = []
    now = datetime.now()

    # ── HEADER BANNER ──
    banner_rows = []
    if logo_path and os.path.exists(logo_path):
        logo_img = Image(logo_path, width=4*cm, height=1.1*cm)
        banner_rows.append(logo_img)

    banner_rows += [
        Spacer(1, 0.3*cm),
        Paragraph(company_name, styles["ReportTitle"]),
        Paragraph(f"Employee Performance Report — {period}", styles["ReportSubtitle"]),
        Spacer(1, 0.3*cm),
        Paragraph(f"Generated: {now.strftime('%A, %d %B %Y at %I:%M %p')}", ParagraphStyle(
            "gen", fontSize=8, fontName="Helvetica", textColor=HexColor("#A5D6A7"), alignment=TA_CENTER)),
    ]

    banner_table = Table([[col] for col in banner_rows], colWidths=[content_w])
    banner_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), primary),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 0.5*cm))

    # ── KPI SUMMARY ──
    if records:
        depts       = len(set(r.department for r in records))
        avg_proj    = round(sum(r.projects for r in records) / len(records), 1)
        avg_sal     = round(sum(r.salary for r in records) / len(records))
        top_perf    = sum(1 for r in records if r.performance in ["Excellent", "Outstanding"])
        kpis = [
            (str(len(records)),  "Total Employees"),
            (str(depts),          "Departments"),
            (str(avg_proj),       "Avg Projects"),
            (f"PKR {avg_sal//1000}K", "Avg Salary"),
            (f"{top_perf}/{len(records)}", "High Performers"),
        ]
        story.append(_kpi_table(kpis, primary, accent, light, content_w))
        story.append(Spacer(1, 0.5*cm))

    # ── MAIN DATA TABLE ──
    story.append(_section_heading("Employee Summary Table", styles, accent))
    story.append(Spacer(1, 0.2*cm))

    col_headers = ["ID", "Name", "Dept", "Role", "Performance", "Projects", "Salary", "Exp (Yrs)", "Status"]
    col_widths   = [1.3*cm, 3.5*cm, 2.2*cm, 3*cm, 2*cm, 1.5*cm, 2.3*cm, 1.5*cm, 1.5*cm]

    header_row = [Paragraph(h, styles["TableHeader"]) for h in col_headers]
    data_rows  = []
    perf_colors = {
        "Outstanding": HexColor("#1B5E20"),
        "Excellent":   HexColor("#2E7D32"),
        "Good":        HexColor("#388E3C"),
        "Average":     HexColor("#F57F17"),
        "Poor":        FAIL_COLOR,
    }

    for i, r in enumerate(records):
        row_data = r.to_table_row()
        perf_para = Paragraph(
            row_data[4],
            ParagraphStyle("pf", fontSize=8, fontName="Helvetica-Bold",
                           textColor=perf_colors.get(row_data[4], TEXT_DARK),
                           alignment=TA_CENTER)
        )
        row = ([Paragraph(cell, styles["TableCell"]) for cell in row_data[:4]]
               + [perf_para]
               + [Paragraph(cell, styles["TableCell"]) for cell in row_data[5:]])
        data_rows.append(row)

    row_style = []
    for i in range(1, len(data_rows) + 1):
        bg = GRAY_LIGHT if i % 2 == 0 else colors.white
        row_style.append(("BACKGROUND", (0, i), (-1, i), bg))

    table = Table([header_row] + data_rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), primary),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",          (0, 0), (-1, -1), 0.3, HexColor("#BDBDBD")),
        ("BOX",           (0, 0), (-1, -1), 0.8, accent),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        *row_style,
    ]))
    story.append(table)
    story.append(Spacer(1, 0.5*cm))

    # ── CHARTS ──
    if chart_paths:
        story.append(PageBreak())
        story.append(_section_heading("Analytics & Visual Insights", styles, accent))
        story.append(Spacer(1, 0.3*cm))

        chart_items = []
        for label, key in [("Performance Ratings", "perf_bar"),
                            ("Department Distribution", "dept_pie"),
                            ("Salary Overview", "salary_bar")]:
            p = chart_paths.get(key)
            if p and os.path.exists(p):
                chart_items.append((label, p))

        for i in range(0, len(chart_items), 2):
            row_charts = chart_items[i:i+2]
            cells = []
            for label, path in row_charts:
                img = Image(path, width=8.5*cm, height=6*cm)
                caption = Paragraph(label, ParagraphStyle("cap", fontSize=8, fontName="Helvetica",
                                                           textColor=GRAY_MID, alignment=TA_CENTER))
                cells.append([img, caption])

            if len(cells) == 1:
                cells.append(["", ""])

            chart_table = Table(
                [[cells[0][0], cells[1][0]], [cells[0][1], cells[1][1]]],
                colWidths=[content_w / 2, content_w / 2],
            )
            chart_table.setStyle(TableStyle([
                ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(chart_table)
            story.append(Spacer(1, 0.3*cm))

    # ── FOOTER ──
    story.append(Spacer(1, 0.5*cm))
    story.append(_divider(accent))
    story.append(Paragraph(
        f"© {now.year} {company_name}  |  ReportGen Pro  |  Confidential Business Document  |  Generated: {now.strftime('%d-%m-%Y %H:%M')}",
        styles["Footer"]
    ))

    doc.build(story)

    if password:
        _encrypt_pdf(output_path, password)

    return output_path


# ─────────────────── ENCRYPTION HELPER ──────────────────
def _encrypt_pdf(path: str, password: str):
    """Encrypt an existing PDF with a user password using pypdf."""
    try:
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_password=password, owner_password=password + "_owner")
        with open(path, "wb") as f:
            writer.write(f)
        print(f"  PDF encrypted with provided password.")
    except Exception as e:
        print(f"  Warning: Encryption failed: {e}")
