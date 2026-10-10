# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
A modular, document-grounded Retrieval-Augmented Generation (RAG) Q&A chatbot that enables users to upload PDF documents, index their content using Google Gemini embeddings and ChromaDB vector database, and ask questions through a clean Streamlit interface with full page-level source citations and strict fallback for unanswerable questions.

## Goals
1. Provide a responsive Streamlit UI for PDF document uploading, document removal, vector indexing, and interactive Q&A.
2. Ingest and extract text from PDFs using PyMuPDF, chunking text into overlapping segments with page reference tracking.
3. Embed document chunks using Gemini `text-embedding-004` and persist them in ChromaDB (`data/chroma_db`).
4. Perform similarity search to retrieve relevant document passages for user questions.
5. Generate accurate, document-grounded answers using `gemini-2.5-flash` with clear source document names and page references.
6. Enforce strict anti-hallucination checks, gracefully handling out-of-scope questions, scanned/empty PDFs, and API failures.

## Non-Goals (Out of Scope)
- Cloud deployment infrastructure setup (Docker/Kubernetes).
- Support for non-PDF file formats (Word, HTML, TXT) in version 1.0.
- User authentication, multi-tenant user accounts, or cloud database sync.
- OCR for image-only/scanned PDFs without extractable text (gracefully reported as empty text).

## Users
- Knowledge workers, researchers, and students who need quick, accurate, source-cited Q&A over internal or reference PDF documents.

## Constraints
- **Language & Runtime:** Python 3.12+
- **SDK & Libraries:** `google-genai` (Gemini API), `chromadb`, `streamlit`, `pymupdf` (`fitz`), `python-dotenv`
- **Security:** API keys strictly loaded from `.env` (`GEMINI_API_KEY`) and never logged or exposed in UI.
- **Persistence:** Local ChromaDB stored in `data/chroma_db` and documents in `data/documents/`.
- **Environment:** Preserve existing `.venv` environment.

## Success Criteria
- [ ] Application starts cleanly via `streamlit run app.py`.
- [ ] PDF document upload, chunking, and embedding creation complete without error.
- [ ] Vector similarity search retrieves top matching passages from ChromaDB.
- [ ] Gemini API generates grounded responses with page numbers and document title citations.
- [ ] Unsupported/out-of-context questions return an explicit refusal without hallucinating.
- [ ] Document list and document removal work seamlessly in Streamlit UI.
