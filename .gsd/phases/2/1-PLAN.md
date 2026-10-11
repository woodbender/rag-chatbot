---
phase: 2
plan: 1
wave: 1
---

# Plan 2.1: Vector Similarity Retrieval & Context Formatting (`rag_pipeline.py`)

## Objective
Implement query vectorization, similarity search against ChromaDB, and context formatting with page-level citations in `rag_pipeline.py`.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md (REQ-05)
- .gsd/ARCHITECTURE.md
- config.py
- ingest.py
- rag_pipeline.py

## Tasks

<task type="auto">
  <name>Implement Vector Query and Retrieval in rag_pipeline.py</name>
  <files>rag_pipeline.py</files>
  <action>
    - Import `config` and relevant functions from `ingest` (`get_embedding`, `get_chroma_collection`).
    - Implement `query_similar_chunks(query: str, top_k: int = 4) -> list[dict]`:
      - Validate `query` is non-empty string; raise ValueError if empty or blank.
      - Check ChromaDB collection count; return empty list immediately if collection is empty.
      - Generate query embedding via `ingest.get_embedding(query)`.
      - Query ChromaDB collection with `query_embeddings=[query_embedding]`, `n_results=min(top_k, count)`.
      - Extract and return structured chunk dictionaries containing:
        - `id`: chunk id
        - `text`: document text
        - `doc_name`: metadata `doc_name`
        - `page`: metadata `page`
        - `distance`: cosine distance score
  </action>
  <verify>.venv\Scripts\python.exe -c "import rag_pipeline; print(hasattr(rag_pipeline, 'query_similar_chunks'))"</verify>
  <done>query_similar_chunks is implemented and handles empty collections as well as vector queries cleanly.</done>
</task>

<task type="auto">
  <name>Implement Context Formatting and Source Extraction</name>
  <files>rag_pipeline.py</files>
  <action>
    - Implement `format_context(chunks: list[dict]) -> tuple[str, list[dict]]`:
      - If `chunks` is empty, return `("", [])`.
      - Build formatted context string where each chunk is labeled with `[Document: <doc_name>, Page: <page>]` followed by the chunk text.
      - Extract and deduplicate source references into a list of dicts: `[{"doc_name": doc_name, "page": page}, ...]`, sorted by doc_name and page.
      - Return tuple of `(formatted_context_string, deduplicated_sources_list)`.
  </action>
  <verify>.venv\Scripts\python.exe -c "import rag_pipeline; c, s = rag_pipeline.format_context([{'doc_name': 'test.pdf', 'page': 1, 'text': 'Hello world'}]); assert '[Document: test.pdf, Page: 1]' in c; assert len(s) == 1; print('CONTEXT_FORMAT_OK')"</verify>
  <done>format_context cleanly formats passages with clear document/page labels and extracts deduplicated source references.</done>
</task>

## Success Criteria
- [ ] `query_similar_chunks` retrieves nearest chunks from ChromaDB with distance metadata and handles empty collections gracefully.
- [ ] `format_context` standardizes context passages with document and page citations and returns deduplicated source references.
