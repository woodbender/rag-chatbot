---
phase: 2
plan: 2
wave: 2
depends_on: ["2.1"]
---

# Plan 2.2: Prompt Engineering, Gemini Generation & Anti-Hallucination Guardrails (`rag_pipeline.py`)

## Objective
Implement system prompts, Gemini `gemini-2.5-flash` grounding generation, anti-hallucination fallback logic, and end-to-end `generate_answer` in `rag_pipeline.py`.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md (REQ-06, REQ-07, REQ-09)
- .gsd/ARCHITECTURE.md
- config.py
- ingest.py
- rag_pipeline.py
- .gsd/phases/2/1-PLAN.md

## Tasks

<task type="auto">
  <name>Implement Grounding Prompt Builder and Gemini LLM Generation</name>
  <files>rag_pipeline.py</files>
  <action>
    - Import `get_genai_client` from `ingest`.
    - Define constant `REFUSAL_MESSAGE = "I cannot answer this question based on the provided documents as the relevant information is not available."`.
    - Implement `build_rag_prompt(query: str, context: str) -> str`:
      - Provide clear instructions to answer strictly based on the context.
      - Mandate citing source document name and page number.
      - Instruct the model to return the explicit refusal phrase if the context is insufficient or question is out of scope.
    - Implement `call_gemini_model(prompt: str) -> str`:
      - Call `client.models.generate_content(model=config.CHAT_MODEL, contents=prompt)`.
      - Return response text string.
  </action>
  <verify>.venv\Scripts\python.exe -c "import rag_pipeline; p = rag_pipeline.build_rag_prompt('What is X?', 'context'); assert 'context' in p; print('PROMPT_BUILDER_OK')"</verify>
  <done>build_rag_prompt and call_gemini_model are implemented with strict anti-hallucination instructions.</done>
</task>

<task type="auto">
  <name>Implement End-to-End generate_answer with Fallback and Error Handling</name>
  <files>rag_pipeline.py</files>
  <action>
    - Implement `generate_answer(query: str, top_k: int = 4) -> dict`:
      - Return structured response: `{"answer": str, "sources": list[dict], "retrieved_chunks": list[dict], "is_refusal": bool}`.
      - If no documents indexed in ChromaDB (count == 0), return clean refusal without making Gemini API call: `{"answer": "No documents have been indexed yet. Please upload and index a PDF first.", "sources": [], "retrieved_chunks": [], "is_refusal": True}`.
      - If query is empty or whitespace, return clear prompt request.
      - Query similar chunks using `query_similar_chunks(query, top_k=top_k)`.
      - Format context and sources using `format_context(chunks)`.
      - If no chunks found, return `REFUSAL_MESSAGE` and empty sources.
      - Call `call_gemini_model(prompt)`.
      - Detect if model output indicates refusal (contains REFUSAL_MESSAGE or phrases like "cannot answer", "not mentioned", "not provided") and set `is_refusal` flag accordingly.
      - Wrap Gemini API calls in try-except block handling `genai.errors.APIError` or general exceptions to return informative error messages.
  </action>
  <verify>.venv\Scripts\python.exe -c "import rag_pipeline; res = rag_pipeline.generate_answer('dummy'); assert 'answer' in res and 'sources' in res and 'is_refusal' in res; print('GENERATE_ANSWER_INTERFACE_OK')"</verify>
  <done>generate_answer coordinates retrieval, grounding prompt construction, fallback refusal checks, and error handling.</done>
</task>

## Success Criteria
- [ ] Strict grounding prompt instructs Gemini to use only provided context and cite document names & pages.
- [ ] Anti-hallucination fallback returns explicit refusal when no documents or matching context exist.
- [ ] `generate_answer` returns structured output with answer, source citations, context chunks, and refusal indicator.
