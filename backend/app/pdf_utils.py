from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PDF_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"

TITLE_STYLE = ParagraphStyle(
    name="Title", fontName="Helvetica-Bold", fontSize=22, leading=26, spaceAfter=14
)
HEADING_STYLE = ParagraphStyle(
    name="Heading", fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=8
)
BODY_STYLE = ParagraphStyle(
    name="Body", fontName="Helvetica", fontSize=14, leading=19, spaceAfter=10
)
WARNING_STYLE = ParagraphStyle(
    name="Warning",
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    spaceAfter=10,
    textColor=colors.red,
)


def generate_fertilizer_pdf(
    prescription_id: int,
    farmer_name: str,
    selected_crop: str,
    soil_type: str,
    items: list,
    excess_nutrient_warnings: list,
) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    file_path = PDF_DIR / f"fertilizer_prescription_{prescription_id}.pdf"

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    story = [
        Paragraph("Fertilizer Prescription", TITLE_STYLE),
        Paragraph(f"Farmer: {farmer_name}", BODY_STYLE),
        Paragraph(f"Crop: {selected_crop.title()}", BODY_STYLE),
        Paragraph(f"Soil Type: {soil_type.title()}", BODY_STYLE),
        Spacer(1, 0.5 * cm),
    ]

    if not items:
        story.append(
            Paragraph(
                "Your soil already has enough Nitrogen, Phosphorus, and Potassium "
                f"for growing {selected_crop}. No extra fertilizer is needed right now.",
                BODY_STYLE,
            )
        )
    else:
        story.append(Paragraph("What to Apply", HEADING_STYLE))
        for item in items:
            story.append(
                Paragraph(
                    f"<b>{item['fertilizer_name']}</b> ({item['chemical_name']})",
                    BODY_STYLE,
                )
            )
            table_data = [
                ["How much", f"{item['quantity_per_acre']} {item['unit']} per acre"],
                ["When to apply", item["timing"]],
                ["Organic option instead", item["organic_alternative"]],
            ]
            table = Table(table_data, colWidths=[5 * cm, 10 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("FONTSIZE", (0, 0), (-1, -1), 13),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ]
                )
            )
            story.append(table)
            story.append(Spacer(1, 0.5 * cm))

    if excess_nutrient_warnings:
        story.append(Paragraph("Please Note", HEADING_STYLE))
        for warning in excess_nutrient_warnings:
            story.append(Paragraph(warning, WARNING_STYLE))

    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "Always wash your hands after handling fertilizer. Keep fertilizer "
            "away from children and animals.",
            BODY_STYLE,
        )
    )

    doc.build(story)
    return file_path
