# Architectural Decision Log (ADR)

## ADR-001: Model Selection & Embeddings
- **Date:** 2026-10-10
- **Status:** Accepted
- **Decision:** Use Google Gemini SDK `google-genai` with `gemini-2.5-flash` for response generation and `gemini-embedding-001` for document chunk vector embeddings.
- **Rationale:** High efficiency, fast latency, cost effectiveness, and strong instruction following for document-grounded RAG tasks.

## ADR-002: Vector Database & Storage
- **Date:** 2026-10-10
- **Status:** Accepted
- **Decision:** Use ChromaDB with persistent disk storage located at `data/chroma_db`.
- **Rationale:** Embedded vector database requiring no external server process, fully compatible with Python 3.12 and Gemini embeddings.

## ADR-003: PDF Parsing Library
- **Date:** 2026-10-10
- **Status:** Accepted
- **Decision:** Use `pymupdf` (`import pymupdf`) for text extraction and page reference mapping.
- **Rationale:** Fast parsing speeds and clean text/page separation compared to legacy options.
