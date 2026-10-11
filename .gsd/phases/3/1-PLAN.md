---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: Streamlit Layout, Sidebar & Document Ingestion/Management UI (`app.py`)

## Objective
Implement Streamlit application foundation, styling, and sidebar document management in `app.py` for uploading PDFs, indexing into ChromaDB, and deleting indexed documents.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md (REQ-08, REQ-09)
- .gsd/ARCHITECTURE.md
- config.py
- ingest.py
- rag_pipeline.py
- app.py

## Tasks

<task type="auto">
  <name>Implement Streamlit Page Configuration, Custom Styling, and PDF Uploader</name>
  <files>app.py</files>
  <action>
    - Configure Streamlit page with `st.set_page_config(page_title="RAG Document Chatbot", page_icon="📚", layout="wide")`.
    - Inject clean CSS styling for sleek modern aesthetics, card badges, source chips, and status containers.
    - Implement sidebar file uploader accepting `.pdf` files.
    - When a file is uploaded and processed:
      - Save PDF file locally to `config.DOCUMENTS_DIR`.
      - Trigger `ingest.ingest_pdf(saved_path)` with progress / status feedback (`st.spinner`).
      - Display total chunks indexed upon success, and notify user if PDF contained no extractable text (e.g. image-only).
  </action>
  <verify>.venv\Scripts\python.exe -c "import app; print(hasattr(app, 'render_sidebar') or 'render_sidebar' in open('app.py').read())"</verify>
  <done>app.py includes page configuration, aesthetic custom CSS, and PDF upload/ingestion pipeline in the sidebar.</done>
</task>

<task type="auto">
  <name>Implement Indexed Document List & Deletion Controls</name>
  <files>app.py</files>
  <action>
    - Retrieve active documents using `ingest.list_indexed_documents()`.
    - Render indexed documents in sidebar with document count metrics.
    - Provide a delete button / action for each indexed document calling `ingest.delete_document(doc_name)` and removing the saved PDF file if present.
    - Refresh application state cleanly on deletion (`st.rerun()`).
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('app.py').read(); assert 'list_indexed_documents' in content and 'delete_document' in content; print('DOC_MANAGEMENT_OK')"</verify>
  <done>Sidebar displays indexed documents and allows user to delete documents from ChromaDB and local disk.</done>
</task>

## Success Criteria
- [ ] Modern UI styling and layout configured with clear navigation.
- [ ] Sidebar file uploader parses, saves, and indexes PDF documents into ChromaDB.
- [ ] Sidebar document list displays indexed files and provides one-click removal.
