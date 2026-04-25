"""
MediScript AI — PDF Report Generator
Generates a professional bilingual (English + Roman Urdu) prescription report
using ReportLab. Zero cost, fully offline.
"""

import io
import json
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ── Color Palette ─────────────────────────────────────────────────────────────
TEAL = colors.HexColor("#00BCD4")
DARK = colors.HexColor("#0D1B2A")
RED = colors.HexColor("#FF4D6D")
YELLOW = colors.HexColor("#FFD700")
GREEN = colors.HexColor("#00C853")
GREY = colors.HexColor("#607D8B")
WHITE = colors.white


def generate_pdf_report(
    drugs: dict,
    interactions: list,
    explanation: dict,
    recommendations: dict,
    double_check: dict,
    scan_id: str = "",
) -> bytes:
    """
    Generate a full bilingual PDF report.
    Returns PDF bytes ready to download.
    """
    if not REPORTLAB_AVAILABLE:
        return b""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    header_style = ParagraphStyle(
        "Header",
        parent=styles["Title"],
        fontSize=22,
        textColor=TEAL,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=GREY,
        spaceAfter=12,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=DARK,
        spaceAfter=6,
        leading=16,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=TEAL,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )

    story.append(Paragraph("MediScript AI — Prescription Report", header_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')} | "
        f"Scan ID: {scan_id[:8] if scan_id else 'N/A'} | "
        "HackData V1 | GDGoC CUI Wah",
        sub_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=TEAL))
    story.append(Spacer(1, 0.3 * cm))

    # ── Doctor / Patient Info ─────────────────────────────────────────────────
    doctor = drugs.get("doctor_name", "Unknown")
    patient = drugs.get("patient_name", "Unknown")
    date = drugs.get("date", "Unknown")
    if any(v != "Unknown" for v in [doctor, patient, date]):
        story.append(Paragraph("Prescription Details", section_style))
        info_data = [
            ["Doctor", doctor],
            ["Patient", patient],
            ["Date", date],
        ]
        info_table = Table(info_data, colWidths=[4 * cm, 13 * cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), TEAL),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, colors.HexColor("#F5F9FA")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Drug List ─────────────────────────────────────────────────────────────
    drug_list = drugs.get("drug_list", [])
    if drug_list:
        story.append(Paragraph(f"Medications Found ({len(drug_list)})", section_style))
        drug_table_data = [["Drug Name", "Dosage", "Frequency", "Duration", "Route"]]
        for d in drug_list:
            drug_table_data.append([
                d.get("name", "?"),
                d.get("dosage", "?"),
                d.get("frequency_readable", d.get("frequency", "?")),
                d.get("duration", "?"),
                d.get("route", "oral"),
            ])
        drug_table = Table(drug_table_data, colWidths=[4 * cm, 3 * cm, 3.5 * cm, 3 * cm, 3 * cm])
        drug_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), TEAL),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F0F8FF")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0E8F0")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(drug_table)
        story.append(Spacer(1, 0.3 * cm))

    # ── Interactions ──────────────────────────────────────────────────────────
    if interactions:
        story.append(Paragraph(f"⚠ Drug Interactions ({len(interactions)})", section_style))
        ix_data = [["Drug 1", "Drug 2", "Severity", "Description"]]
        for ix in interactions:
            sev = ix.get("severity", "MODERATE")
            ix_data.append([
                ix.get("drug1", "?"),
                ix.get("drug2", "?"),
                sev,
                (ix.get("description", ""))[:80] + ("..." if len(ix.get("description", "")) > 80 else ""),
            ])
        ix_table = Table(ix_data, colWidths=[3 * cm, 3 * cm, 3 * cm, 7.5 * cm])
        sev_colors = {"SEVERE": RED, "MODERATE": YELLOW, "MILD": GREEN}

        ix_style = [
            ("BACKGROUND", (0, 0), (-1, 0), RED),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FFCCCC")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]
        for i, ix in enumerate(interactions, start=1):
            sev = ix.get("severity", "MODERATE")
            c = sev_colors.get(sev, YELLOW)
            ix_style.append(("TEXTCOLOR", (2, i), (2, i), c))
            ix_style.append(("FONTNAME", (2, i), (2, i), "Helvetica-Bold"))

        ix_table.setStyle(TableStyle(ix_style))
        story.append(ix_table)
        story.append(Spacer(1, 0.3 * cm))
    else:
        story.append(Paragraph("✓ No drug interactions detected.", body_style))

    # ── English Explanation ───────────────────────────────────────────────────
    if explanation.get("english"):
        story.append(Paragraph("English Explanation", section_style))
        story.append(Paragraph(explanation["english"], body_style))
        story.append(Spacer(1, 0.2 * cm))

    # ── Roman Urdu Explanation ────────────────────────────────────────────────
    if explanation.get("urdu"):
        story.append(Paragraph("Roman Urdu / رومن اردو", section_style))
        story.append(Paragraph(explanation["urdu"], body_style))
        story.append(Spacer(1, 0.2 * cm))

    # ── Warnings ─────────────────────────────────────────────────────────────
    warnings = explanation.get("warnings", [])
    if warnings:
        story.append(Paragraph("⚠ Warnings", section_style))
        for w in warnings:
            story.append(Paragraph(f"• {w}", body_style))
        story.append(Spacer(1, 0.2 * cm))

    # ── Tips ─────────────────────────────────────────────────────────────────
    tips = explanation.get("tips", [])
    if tips:
        story.append(Paragraph("Tips for Safe Use", section_style))
        for t in tips:
            story.append(Paragraph(f"✓ {t}", body_style))
        story.append(Spacer(1, 0.2 * cm))

    # ── Recommendations ───────────────────────────────────────────────────────
    if recommendations:
        dietary = recommendations.get("dietary", [])
        lifestyle = recommendations.get("lifestyle", [])
        if dietary or lifestyle:
            story.append(Paragraph("Recommendations", section_style))
            for d in dietary:
                story.append(Paragraph(f"• {d}", body_style))
            for l in lifestyle:
                story.append(Paragraph(f"• {l}", body_style))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREY))
    story.append(Paragraph(
        "MediScript AI — Pakistan's First AI Prescription Analyzer | "
        "Project Idea: Hamza Ali | Team: Muhammad Umair Malik, Shahzaib Shoaib Rathore | "
        "HackData V1 | GDGoC CUI Wah | This report is for informational purposes only. "
        "Always follow your doctor's instructions.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=GREY),
    ))

    doc.build(story)
    return buffer.getvalue()
