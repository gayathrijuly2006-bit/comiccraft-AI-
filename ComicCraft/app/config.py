from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "ComicCraft")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# The uploaded documentation selected Gemini Flash + Gemini Pro. The original
# 1.5 model IDs are now legacy, so these defaults are current stable IDs and
# remain configurable through .env.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_OUTLINE_MODEL = os.getenv("GEMINI_OUTLINE_MODEL", "gemini-3.8-flash")
GEMINI_STORY_MODEL = os.getenv("GEMINI_STORY_MODEL", "gemini-3.8-flash")

HF_TOKEN = os.getenv("HF_TOKEN", os.getenv("HF_API_KEY", "")).strip()
HF_PROVIDER = os.getenv("HF_PROVIDER", "auto")
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
IMAGE_BACKEND = os.getenv("IMAGE_BACKEND", "hf").lower()  # hf | local | mock
LOCAL_IMAGE_MODEL = os.getenv("LOCAL_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")

USE_MOCK_AI = os.getenv("USE_MOCK_AI", "auto").lower()  # true | false | auto
MOCK_IF_KEYS_MISSING = USE_MOCK_AI in {"auto", "true"}

MAX_PANELS = int(os.getenv("MAX_PANELS", "5"))
IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "768"))
IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "768"))

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"

for directory in (PANELS_DIR, EXPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
