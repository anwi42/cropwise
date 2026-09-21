import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agriplatform")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

SUPPORTED_LANGUAGES = [
    "english",
    "hindi",
    "marathi",
    "telugu",
    "tamil",
    "punjabi",
    "gujarati",
    "kannada",
]
