import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory paths
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", str(BASE_DIR / "data" / "chroma_db"))
DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR", str(BASE_DIR / "data" / "documents"))

# Model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")

# Ingestion configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "document_collection")


def validate_config() -> bool:
    """Validate critical environment configuration.

    Raises:
        ValueError: If GEMINI_API_KEY is not set or empty.

    Returns:
        bool: True if configuration is valid.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "" or GEMINI_API_KEY == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is missing or invalid. "
            "Please create a .env file and set GEMINI_API_KEY."
        )

    # Ensure data directories exist
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    return True
