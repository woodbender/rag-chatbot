# Document-Based RAG Q&A Chatbot

A Retrieval-Augmented Generation (RAG) Q&A chatbot built with Python 3.12, Gemini API, ChromaDB, PyMuPDF, and Streamlit.

## Setup

1. Copy `.env.example` to `.env` and set your `GEMINI_API_KEY`.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place PDF files into `data/documents/`.
4. Run document ingestion:
   ```bash
   python ingest.py
   ```
5. Launch the application:
   ```bash
   streamlit run app.py
   ```
