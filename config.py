import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "decision-ai-secret-key-2026")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    DATABASE_PATH = BASE_DIR / "decision_ai.db"
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    PORT = int(os.getenv("PORT", 5000))

