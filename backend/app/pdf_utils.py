from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Optional

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
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
FOOTER_STYLE = ParagraphStyle(
    name="Footer",
    fontName="Helvetica-Oblique",
    fontSize=11,
    leading=14,
    textColor=colors.grey,
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


def _qr_flowable(data: str, size_cm: float = 3.5) -> Image:
    qr = qrcode.QRCode(border=1)
    qr.add_data(data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    return Image(buffer, width=size_cm * cm, height=size_cm * cm)


def generate_yield_certificate_pdf(
    certificate_id: int,
    farmer_name: str,
    village: Optional[str],
    taluka: Optional[str],
    district: Optional[str],
    state: Optional[str],
    farm_size: Optional[float],
    soil_type: Optional[str],
    crop_type: str,
    crop_variety: Optional[str],
    predicted_yield_min: float,
    predicted_yield_max: float,
    confidence_score: float,
    soil_health_score: Optional[int],
    soil_health_zone: Optional[str],
    weather_risk_text: str,
    document_hash: str,
    verification_code: str,
    verify_url: str,
    generated_at: datetime,
    bank_officer_name: str,
) -> Path:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    file_path = PDF_DIR / f"yield_certificate_{certificate_id}.pdf"

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    location = ", ".join(part for part in [village, taluka, district, state] if part)
    crop_display = f"{crop_type.title()} ({crop_variety})" if crop_variety else crop_type.title()

    detail_rows = [
        ["Farmer Name", farmer_name],
        ["Location", location or "Not on file"],
        ["Farm Size", f"{farm_size} acres" if farm_size is not None else "Not on file"],
        ["Soil Type", soil_type.title() if soil_type else "Not on file"],
        ["Current Crop", crop_display],
        ["Predicted Yield Range", f"{predicted_yield_min} - {predicted_yield_max} tons/acre"],
        ["Confidence Score", f"{confidence_score}%"],
        [
            "Soil Health",
            f"{soil_health_score} ({soil_health_zone} Zone)" if soil_health_score is not None else "Not scored",
        ],
        ["Weather Risk Assessment", weather_risk_text],
    ]
    detail_table = Table(detail_rows, colWidths=[5.5 * cm, 9.5 * cm])
    detail_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )

    story = [
        Paragraph("CropWise", TITLE_STYLE),
        Paragraph("AI-Verified Yield Certificate", HEADING_STYLE),
        Spacer(1, 0.3 * cm),
        detail_table,
        Spacer(1, 0.7 * cm),
        Paragraph("Document Verification", HEADING_STYLE),
        Paragraph(f"Document Hash (SHA-256): {document_hash}", BODY_STYLE),
        Paragraph(f"Verification Code: {verification_code}", BODY_STYLE),
        Spacer(1, 0.3 * cm),
        _qr_flowable(verify_url),
        Paragraph(f"Scan this code or visit: {verify_url}", BODY_STYLE),
        Spacer(1, 0.5 * cm),
        Paragraph(
            f"Generated on {generated_at.strftime('%d %b %Y, %I:%M %p')} by {bank_officer_name}",
            BODY_STYLE,
        ),
        Spacer(1, 0.7 * cm),
        Paragraph("Generated by CropWise AI Platform", FOOTER_STYLE),
    ]

    doc.build(story)
    return file_path
