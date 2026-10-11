---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Automated Integration Test Suite for End-to-End RAG Pipeline

## Objective
Build and run a comprehensive automated integration test suite `test_integration.py` to empirically validate PDF ingestion, chunking, ChromaDB vector querying, context formatting, source citations, document deletion, and anti-hallucination guardrails.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md (REQ-01 through REQ-09)
- config.py
- ingest.py
- rag_pipeline.py
- app.py

## Tasks

<task type="auto">
  <name>Create Automated Integration Test Suite</name>
  <files>test_integration.py</files>
  <action>
    - Create `test_integration.py` using Python's standard `unittest` framework.
    - Test 1: Config loading, directory creation, and API key validation.
    - Test 2: PDF text extraction and chunking with 1-indexed page metadata.
    - Test 3: ChromaDB vector storage operations (adding chunks, querying with cosine distance, retrieving metadatas).
    - Test 4: Context formatting and source deduplication (`format_context`).
    - Test 5: Anti-hallucination refusal detection and prompt structure (`build_rag_prompt`, `is_refusal_response`).
    - Test 6: Document deletion and index listing consistency (`delete_document`, `list_indexed_documents`).
  </action>
  <verify>.venv\Scripts\python.exe -m unittest test_integration.py</verify>
  <done>All integration tests in test_integration.py pass with zero failures.</done>
</task>

## Success Criteria
- [ ] Automated integration test suite covers ingestion, vector storage, context formatting, and guardrails.
- [ ] All test cases execute cleanly and pass via the test runner.
