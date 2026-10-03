"""Central settings, loaded from .env."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
WORKSPACE_ROOT = BASE_DIR / "workspace"
APPROVED_DIR = BASE_DIR / "approved"
SAMPLES_DIR = BASE_DIR / "samples"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
LOW_TOKEN_MODE = os.getenv("LOW_TOKEN_MODE", "false").lower() == "true"
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "").strip()
USE_DOCKER = os.getenv("USE_DOCKER", "true").lower() == "true"
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))

SANDBOX_IMAGE = "aegisguard-sandbox"
SANDBOX_TIMEOUT = 30
SANDBOX_MEMORY = "256m"

# Uploaded-project safety limits. Uploaded code is parsed only; it is never executed
# by the project scanner. The existing sample demo may still use the sandbox workflow.
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(15 * 1024 * 1024)))
MAX_EXTRACTED_BYTES = int(os.getenv("MAX_EXTRACTED_BYTES", str(50 * 1024 * 1024)))
MAX_PROJECT_FILES = int(os.getenv("MAX_PROJECT_FILES", "500"))
MAX_PYTHON_FILES = int(os.getenv("MAX_PYTHON_FILES", "200"))
MAX_SINGLE_FILE_BYTES = int(os.getenv("MAX_SINGLE_FILE_BYTES", str(1024 * 1024)))
