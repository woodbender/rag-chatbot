# ROADMAP.md

> **Current Phase**: Phase 3 Complete
> **Milestone**: v1.0

## Must-Haves (from SPEC)
- [x] PDF document upload, text extraction, chunking, and embedding creation.
- [x] Persistent ChromaDB vector storage for fast context retrieval.
- [x] Gemini API powered Q&A with page-level source citations.
- [x] Anti-hallucination fallback for out-of-scope or unanswerable queries.
- [x] Clean Streamlit user interface with document management/removal support.

## Phases

### Phase 1: Foundation & Ingestion Engine
**Status**: ✅ Complete
**Objective**: Build `config.py` and `ingest.py` to handle PDF text extraction via `pymupdf`, chunking with page metadata, Gemini embeddings using `text-embedding-004`, and persistence/deletion in ChromaDB.
**Requirements**: REQ-01, REQ-02, REQ-03, REQ-04

### Phase 2: RAG Pipeline & Gemini Grounding
**Status**: ✅ Complete
**Objective**: Build `rag_pipeline.py` to perform ChromaDB similarity search, construct context-augmented prompts, generate answers via `google-genai` (`gemini-2.5-flash`), and enforce strict fallback for unsupported queries.
**Requirements**: REQ-05, REQ-06, REQ-07

### Phase 3: Streamlit Interface & Document Management
**Status**: ✅ Complete
**Objective**: Implement `app.py` delivering a polished Streamlit user interface for document upload, document collection management/deletion, chat interface with visible citations, and error messaging.
**Requirements**: REQ-08, REQ-09

### Phase 4: Integration Verification & End-to-End Testing
**Status**: ⬜ Not Started
**Objective**: Empirically test and verify full workflow from PDF ingestion to vector search, source-grounded answering, out-of-scope refusals, and UI document deletion.
**Requirements**: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09
