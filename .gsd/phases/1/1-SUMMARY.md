# Plan 1.1 Summary: Configuration Module & PDF Ingestion Core

## Work Completed
- **Created `config.py`**:
  - Environment variable loader using `python-dotenv`.
  - Defined system constants (`GEMINI_API_KEY`, `CHROMA_DB_DIR`, `DOCUMENTS_DIR`, `EMBEDDING_MODEL`, `CHAT_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `COLLECTION_NAME`).
  - Added `validate_config()` helper to verify API key presence and initialize required directories.
- **Implemented PDF extraction and chunking in `ingest.py`**:
  - `extract_text_from_pdf(pdf_path)` using `pymupdf`.
  - Page-indexed text extraction preserving 1-indexed page numbers.
  - `chunk_text(pages_data, doc_name)` generating overlapping text chunks with rich metadata (`id`, `text`, `doc_name`, `page`).

## Verification Output
- `config.py`: Verified via Python import and environment path check.
- `ingest.py`: Verified via automated unit test creating 8 overlapping chunks from sample page text.

## Commits
- `a1965a8 feat(phase-1): add config module with environment validation`
- `9b2fe4e feat(phase-1): implement PDF text extraction and chunking in ingest.py`
