---
phase: 1
plan: 2
wave: 2
depends_on: ["1.1"]
---

# Plan 1.2: Gemini Embeddings & ChromaDB Persistence (`ingest.py` Integration)

## Objective
Implement Gemini embedding generation and ChromaDB persistent storage in `ingest.py` to support indexing PDF documents and deleting indexed documents.

## Context
- `.gsd/SPEC.md`
- `.gsd/REQUIREMENTS.md` (REQ-03, REQ-04)
- `.gsd/ARCHITECTURE.md`
- `config.py`
- `ingest.py`
- `.gsd/phases/1/1-PLAN.md`

## Tasks

<task type="auto">
  <name>Implement Gemini Embedding Adapter & ChromaDB Store</name>
  <files>ingest.py</files>
  <action>
    - Import `google.genai` and `chromadb`.
    - Implement embedding generator function `get_embedding(text: str) -> list[float]` using `google.genai.Client(api_key=config.GEMINI_API_KEY).models.embed_content(model=config.EMBEDDING_MODEL, contents=text)`.
    - Implement batch embedding function `get_embeddings_batch(texts: list[str]) -> list[list[float]]` handling batching gracefully.
    - Implement ChromaDB persistent client helper `get_chroma_collection()` using `chromadb.PersistentClient(path=config.CHROMA_DB_DIR)` and `get_or_create_collection(name=config.COLLECTION_NAME)`.
  </action>
  <verify>.venv\Scripts\python.exe -c "import ingest; print(hasattr(ingest, 'get_chroma_collection'))"</verify>
  <done>get_chroma_collection and get_embedding functions are defined and return valid handles.</done>
</task>

<task type="auto">
  <name>Implement Document Ingestion & Deletion Pipeline Functions</name>
  <files>ingest.py</files>
  <action>
    - Implement `ingest_pdf(pdf_path: str) -> int`:
      - Extract pages using `extract_text_from_pdf`.
      - Chunk text using `chunk_text`.
      - Delete existing chunks for `doc_name` if re-ingesting.
      - Generate embeddings for chunks.
      - Add ids, embeddings, documents, and metadatas (`{"doc_name": doc_name, "page": page}`) to ChromaDB collection.
      - Return total chunk count added.
    - Implement `delete_document(doc_name: str) -> None`:
      - Query collection or delete entries where `doc_name == target_doc_name`.
    - Implement `list_indexed_documents() -> list[str]`:
      - Retrieve unique `doc_name` values currently stored in the ChromaDB collection metadata.
  </action>
  <verify>.venv\Scripts\python.exe -c "import ingest; print(hasattr(ingest, 'ingest_pdf') and hasattr(ingest, 'delete_document') and hasattr(ingest, 'list_indexed_documents'))"</verify>
  <done>ingest_pdf, delete_document, and list_indexed_documents are implemented and pass function presence verification.</done>
</task>

## Success Criteria
- [ ] ChromaDB persistent client stores embedded PDF chunks under `data/chroma_db`.
- [ ] `ingest_pdf` extracts, embeds, and stores chunks with metadata in ChromaDB.
- [ ] `delete_document` cleans up all chunks for a given document.
- [ ] `list_indexed_documents` returns the list of unique document names indexed.
