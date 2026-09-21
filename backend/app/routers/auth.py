import bcrypt
from fastapi import APIRouter, HTTPException

from app.database import get_db_cursor
from app.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse

router = APIRouter(prefix="/api", tags=["auth"])


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


@router.post("/register", response_model=RegisterResponse)
def register(payload: RegisterRequest):
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id FROM farmers WHERE phone = %s", (payload.phone,))
        existing = cur.fetchone()
        if existing:
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "message": "Phone number already registered",
                },
            )

        hashed = hash_password(payload.password)

        cur.execute(
            """
            INSERT INTO farmers
                (name, phone, password, preferred_language, village, taluka, district, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                payload.name,
                payload.phone,
                hashed,
                payload.preferred_language,
                payload.village,
                payload.taluka,
                payload.district,
                payload.state,
            ),
        )
        farmer_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO farms
                (farmer_id, farm_size, soil_type, water_source, crops_grown_before)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                farmer_id,
                payload.farm_size,
                payload.soil_type,
                payload.water_source,
                payload.crops_grown_before,
            ),
        )

    return RegisterResponse(
        success=True,
        message="Farmer registered successfully",
        farmer_id=farmer_id,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT id, name, password, preferred_language FROM farmers WHERE phone = %s",
            (payload.phone,),
        )
        farmer = cur.fetchone()

    if farmer is None or not verify_password(payload.password, farmer["password"]):
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "message": "Invalid phone number or password",
            },
        )

    return LoginResponse(
        success=True,
        message="Login successful",
        farmer_id=farmer["id"],
        name=farmer["name"],
        preferred_language=farmer["preferred_language"],
    )
