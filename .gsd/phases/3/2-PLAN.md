---
phase: 3
plan: 2
wave: 2
depends_on: ["3.1"]
---

# Plan 3.2: Interactive Chat Interface, Citation Rendering & Error Handling (`app.py`)

## Objective
Implement conversational chat history in `st.session_state`, user query processing via `rag_pipeline.generate_answer()`, page-level citation cards/badges, and defensive error handling in `app.py`.

## Context
- .gsd/SPEC.md
- .gsd/REQUIREMENTS.md (REQ-08, REQ-09)
- .gsd/ARCHITECTURE.md
- config.py
- ingest.py
- rag_pipeline.py
- app.py
- .gsd/phases/3/1-PLAN.md

## Tasks

<task type="auto">
  <name>Implement Chat Session State and Interactive Conversation UI</name>
  <files>app.py</files>
  <action>
    - Initialize chat messages in `st.session_state.messages` if not present.
    - Render chat message history using `st.chat_message("user")` and `st.chat_message("assistant")`.
    - Accept input using `st.chat_input("Ask a question about your indexed documents...")`.
    - On input submit:
      - Append user question to session state and render immediately.
      - Invoke `rag_pipeline.generate_answer(prompt)`.
      - Render assistant answer.
      - If sources exist and response is not a refusal, display clear citation chips/badges (document name and page number) and an expandable view showing retrieved text snippets.
      - Append assistant response payload (including citations) to session state.
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('app.py').read(); assert 'generate_answer' in content and 'st.chat_input' in content; print('CHAT_UI_OK')"</verify>
  <done>Interactive chat interface manages conversation turns and renders answers alongside formatted citation badges.</done>
</task>

<task type="auto">
  <name>Implement Error Banners, Empty State Guides, and API Key Validation</name>
  <files>app.py</files>
  <action>
    - Check API key status on startup using `config.validate_config()`.
    - If `GEMINI_API_KEY` is missing or invalid, render a prominent warning banner with instructions on adding the key to `.env`.
    - If no documents are currently indexed in ChromaDB, render a welcoming empty state guiding the user to upload a PDF in the sidebar before chatting.
    - Provide a "Clear Chat History" button in the sidebar to reset `st.session_state.messages`.
    - Catch and display friendly notifications for unreadable PDFs, network timeouts, or vector DB issues.
  </action>
  <verify>.venv\Scripts\python.exe -c "content = open('app.py').read(); assert 'validate_config' in content and 'Clear Chat' in content; print('SAFEGUARDS_OK')"</verify>
  <done>Empty state instructions, API key alerts, chat clearing, and error handlers are active.</done>
</task>

## Success Criteria
- [ ] Users can submit queries via `st.chat_input` and receive grounded answers from `rag_pipeline`.
- [ ] Citations are displayed with document names and page numbers, plus expandable chunk previews.
- [ ] Refusal answers and empty states guide the user cleanly without application crash.
- [ ] API key configuration check alerts user if `.env` key is absent.
