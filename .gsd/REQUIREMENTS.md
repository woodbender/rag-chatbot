# REQUIREMENTS.md

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| REQ-01 | Environment setup and config module (`config.py`) loading `GEMINI_API_KEY`, Chroma DB path, and model parameters from `.env`. | SPEC Goal 1 & Constraints | Complete |
| REQ-02 | PDF text extraction and chunking module (`ingest.py`) using `pymupdf` to extract text with page numbers and split into overlapping chunks. | SPEC Goal 2 | Complete |
| REQ-03 | Custom ChromaDB embedding adapter or Gemini `text-embedding-004` embedding function to store and query vectors in ChromaDB persistent collection. | SPEC Goal 3 | Complete |
| REQ-04 | Document ingestion pipeline in `ingest.py` supporting indexing new documents and deleting existing documents from ChromaDB. | SPEC Goal 2 & Core Feature 8 | Complete |
| REQ-05 | RAG pipeline module (`rag_pipeline.py`) performing similarity search over ChromaDB and prompt construction with retrieved context passages. | SPEC Goal 4 | Pending |
| REQ-06 | Gemini answer generation (`rag_pipeline.py`) using `google-genai` SDK (`gemini-2.5-flash`), formatting answers with source document and page references. | SPEC Goal 5 | Pending |
| REQ-07 | Strict anti-hallucination fallback returning explicit refusal when retrieved context is insufficient or question is out of scope. | SPEC Goal 6 | Pending |
| REQ-08 | Streamlit frontend (`app.py`) providing PDF document upload, document collection management/removal, chat interface, and citation displays. | SPEC Goal 1 | Pending |
| REQ-09 | Robust error handling for empty/scanned PDFs, missing API keys, vector DB corruption, and Gemini API rate limit / network errors. | SPEC Goal 6 | Pending |
