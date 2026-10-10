---
phase: 1
plan: 1
wave: 1
---

# Plan 1.1: Configuration Module & PDF Ingestion Core (`config.py` & `ingest.py` Extraction)

## Objective
Create the central configuration module `config.py` and the core PDF text extraction and chunking logic in `ingest.py` using PyMuPDF (`pymupdf`).

## Context
- `.gsd/SPEC.md`
- `.gsd/REQUIREMENTS.md` (REQ-01, REQ-02)
- `.gsd/ARCHITECTURE.md`
- `config.py`
- `ingest.py`

## Tasks

<task type="auto">
  <name>Create Configuration Module</name>
  <files>config.py</files>
  <action>
    - Populate `config.py` to load environment variables via `python-dotenv`.
    - Define configuration constants:
      - `GEMINI_API_KEY` (string, loaded from `.env`)
      - `CHROMA_DB_DIR` (default: `"data/chroma_db"`)
      - `DOCUMENTS_DIR` (default: `"data/documents"`)
      - `EMBEDDING_MODEL` (default: `"text-embedding-004"`)
      - `CHAT_MODEL` (default: `"gemini-2.5-flash"`)
      - `CHUNK_SIZE` (default: 1000)
      - `CHUNK_OVERLAP` (default: 200)
      - `COLLECTION_NAME` (default: `"document_collection"`)
    - Add helper `validate_config()` that checks if `GEMINI_API_KEY` is present and non-empty, raising a clear runtime error if missing.
  </action>
  <verify>.venv\Scripts\python.exe -c "import config; config.validate_config(); print('CONFIG_VALIDATED')"</verify>
  <done>config.py successfully exports configuration variables and passes validation check.</done>
</task>

<task type="auto">
  <name>Implement PDF Extraction & Chunking Logic</name>
  <files>ingest.py</files>
  <action>
    - Import `pymupdf` and `config`.
    - Implement `extract_text_from_pdf(pdf_path: str) -> list[dict]` which opens PDF via `pymupdf.open(pdf_path)` and extracts `(page_num, text)` for each page.
    - Handle scanned or empty pages gracefully by returning empty list / logging warning without crashing.
    - Implement `chunk_text(pages_text: list[dict], chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> list[dict]`.
    - Each chunk dictionary must contain:
      - `"id"`: Unique chunk identifier (e.g. `f"{doc_name}_p{page_num}_c{idx}"`)
      - `"text"`: The chunk text string
      - `"doc_name"`: Basename of the PDF file
      - `"page"`: 1-indexed page number where the chunk originated
  </action>
  <verify>.venv\Scripts\python.exe -c "import ingest; print(hasattr(ingest, 'extract_text_from_pdf') and hasattr(ingest, 'chunk_text'))"</verify>
  <done>extract_text_from_pdf and chunk_text functions are exported and pass unit verification.</done>
</task>

## Success Criteria
- [ ] `config.py` validates `GEMINI_API_KEY` and sets all system constants.
- [ ] `ingest.py` extracts text from PDF pages with 1-indexed page metadata.
- [ ] `chunk_text` produces overlapping text chunks with document name and page number metadata.
