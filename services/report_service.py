from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from database.db_config import REPORT_DIR


def generate_pdf_report(result: dict) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    file_name = f"analysis_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    report_path = REPORT_DIR / file_name

    doc = SimpleDocTemplate(str(report_path), pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SmallBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
        )
    )
    elements = [
        Paragraph("AI Resume Screening Report", styles["Title"]),
        Spacer(1, 14),
        Paragraph(f"Candidate: {result.get('candidate_name', 'N/A')}", styles["Heading2"]),
        Paragraph(f"Job Role: {result.get('job_title', 'N/A')}", styles["Normal"]),
        Paragraph(f"Match Score: {result.get('match_score', 0):.2f}%", styles["Normal"]),
        Paragraph(f"Recommendation: {result.get('recommendation', 'N/A')}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph(result.get("summary", ""), styles["BodyText"]),
        Spacer(1, 14),
    ]

    breakdown_rows = [
        ["Metric", "Score"],
        ["Skill Coverage", f"{result.get('skill_coverage', 0):.2f}%"],
        ["TF-IDF Similarity", f"{result.get('tfidf_similarity', 0):.2f}%"],
        ["Keyword Coverage", f"{result.get('keyword_score', 0):.2f}%"],
        ["Resume Completeness", f"{result.get('profile_strength', 0):.2f}%"],
    ]
    breakdown_table = Table(breakdown_rows, colWidths=[240, 120])
    breakdown_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8fbff")),
            ]
        )
    )
    elements.extend([Paragraph("Score Breakdown", styles["Heading2"]), breakdown_table, Spacer(1, 14)])

    rows = [
        ["Category", "Details"],
        ["Matched Skills", Paragraph(", ".join(result.get("matched_skills", [])) or "None", styles["SmallBody"])],
        ["Missing Skills", Paragraph(", ".join(result.get("missing_skills", [])) or "None", styles["SmallBody"])],
        ["Recommended Skills", Paragraph(", ".join(result.get("recommended_skills", [])) or "None", styles["SmallBody"])],
        ["Keyword Matches", Paragraph(", ".join(result.get("keyword_matches", [])) or "None", styles["SmallBody"])],
    ]
    table = Table(rows, colWidths=[120, 360])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return report_path
