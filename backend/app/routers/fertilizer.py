import psycopg2.extras
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.database import get_db_cursor
from app.pdf_utils import PDF_DIR, generate_fertilizer_pdf
from app.schemas import FertilizerRequest, FertilizerResponse
from app.soil_scoring import NUTRIENT_LABELS, score_nutrient

router = APIRouter(prefix="/api/soil", tags=["fertilizer"])

NUTRIENT_FERTILIZER_MAP = {
    "nitrogen": "Urea",
    "phosphorus": "DAP",
    "potassium": "MOP",
}


@router.post("/fertilizer", response_model=FertilizerResponse)
def prescribe_fertilizer(payload: FertilizerRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            """
            SELECT id, nitrogen, phosphorus, potassium
            FROM soil_reports
            WHERE id = %s AND farmer_id = %s
            """,
            (payload.soil_report_id, payload.farmer_id),
        )
        soil_report = cur.fetchone()
        if soil_report is None:
            raise HTTPException(
                status_code=404, detail="Soil report not found for this farmer"
            )

        cur.execute("SELECT id, name FROM farmers WHERE id = %s", (payload.farmer_id,))
        farmer = cur.fetchone()
        if farmer is None:
            raise HTTPException(status_code=404, detail="Farmer not found")

        cur.execute(
            """
            SELECT soil_type FROM farms
            WHERE farmer_id = %s AND soil_type IS NOT NULL AND soil_type <> ''
            ORDER BY id DESC LIMIT 1
            """,
            (payload.farmer_id,),
        )
        farm = cur.fetchone()
        if farm is None:
            raise HTTPException(
                status_code=400,
                detail="This farmer has no soil_type on file; cannot look up fertilizer guidelines",
            )
        soil_type = farm["soil_type"]

        cur.execute(
            """
            SELECT nutrient, min_value, max_value
            FROM icar_soil_standards
            WHERE crop_name = %s AND nutrient IN ('nitrogen', 'phosphorus', 'potassium')
            """,
            (payload.selected_crop,),
        )
        standard_rows = cur.fetchall()
        if not standard_rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No ICAR soil standards found for crop '{payload.selected_crop}'. "
                    "Supported crops: wheat, rice, tomato, onion, soybean, maize, "
                    "cotton, sugarcane."
                ),
            )
        standards = {
            row["nutrient"]: (float(row["min_value"]), float(row["max_value"]))
            for row in standard_rows
        }

        cur.execute(
            """
            SELECT fertilizer_name, chemical_name, quantity_per_acre, timing, organic_alternative
            FROM icar_fertilizer_guidelines
            WHERE crop_name = %s AND soil_type = %s
            """,
            (payload.selected_crop, soil_type),
        )
        guideline_rows = cur.fetchall()
        if not guideline_rows:
            cur.execute(
                "SELECT DISTINCT soil_type FROM icar_fertilizer_guidelines WHERE crop_name = %s",
                (payload.selected_crop,),
            )
            available = [row["soil_type"] for row in cur.fetchall()]
            raise HTTPException(
                status_code=404,
                detail=(
                    f"No fertilizer guidelines found for '{payload.selected_crop}' on "
                    f"'{soil_type}' soil. Available soil types for this crop: {available}."
                ),
            )
        guidelines_by_name = {row["fertilizer_name"]: row for row in guideline_rows}

        soil_values = {
            "nitrogen": float(soil_report["nitrogen"]),
            "phosphorus": float(soil_report["phosphorus"]),
            "potassium": float(soil_report["potassium"]),
        }

        items = []
        excess_nutrient_warnings = []

        for nutrient, value in soil_values.items():
            min_v, max_v = standards[nutrient]
            status, _ = score_nutrient(value, min_v, max_v)

            if status == "deficient":
                fertilizer_key = NUTRIENT_FERTILIZER_MAP[nutrient]
                guideline = guidelines_by_name.get(fertilizer_key)
                if guideline is not None:
                    items.append(
                        {
                            "nutrient": nutrient,
                            "status": status,
                            "fertilizer_name": guideline["fertilizer_name"],
                            "chemical_name": guideline["chemical_name"],
                            "quantity_per_acre": float(guideline["quantity_per_acre"]),
                            "unit": "kg",
                            "timing": guideline["timing"],
                            "organic_alternative": guideline["organic_alternative"],
                        }
                    )
            elif status == "excess":
                label = NUTRIENT_LABELS[nutrient]
                excess_nutrient_warnings.append(
                    f"{label} levels are already above the ideal range for "
                    f"{payload.selected_crop}. Avoid adding extra {label.lower()} "
                    "fertilizer this season."
                )

        message = (
            f"Your soil already has enough Nitrogen, Phosphorus, and Potassium for "
            f"{payload.selected_crop}. No extra fertilizer is needed right now."
            if not items
            else f"Fertilizer plan generated for {payload.selected_crop} on {soil_type} soil."
        )

        cur.execute(
            """
            INSERT INTO fertilizer_prescriptions (farmer_id, soil_report_id, selected_crop, prescription)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.farmer_id,
                payload.soil_report_id,
                payload.selected_crop,
                psycopg2.extras.Json(
                    {
                        "soil_type_used": soil_type,
                        "items": items,
                        "excess_nutrient_warnings": excess_nutrient_warnings,
                        "message": message,
                    }
                ),
            ),
        )
        prescription_id = cur.fetchone()["id"]

    generate_fertilizer_pdf(
        prescription_id=prescription_id,
        farmer_name=farmer["name"],
        selected_crop=payload.selected_crop,
        soil_type=soil_type,
        items=items,
        excess_nutrient_warnings=excess_nutrient_warnings,
    )

    return FertilizerResponse(
        success=True,
        fertilizer_prescription_id=prescription_id,
        selected_crop=payload.selected_crop,
        soil_type_used=soil_type,
        items=items,
        excess_nutrient_warnings=excess_nutrient_warnings,
        message=message,
        pdf_download_url=f"/api/soil/fertilizer/{prescription_id}/pdf",
    )


@router.get("/fertilizer/{prescription_id}/pdf")
def download_fertilizer_pdf(prescription_id: int):
    file_path = PDF_DIR / f"fertilizer_prescription_{prescription_id}.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found for this prescription")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"fertilizer_prescription_{prescription_id}.pdf",
    )
