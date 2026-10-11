import os
from pathlib import Path
from typing import List, Dict, Any
import streamlit as st

import config
import ingest
import rag_pipeline

# Configure Streamlit page
st.set_page_config(
    page_title="RAG Document Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling and citations
st.markdown("""
<style>
    /* Global styling */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    
    /* Citation chip */
    .citation-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59, 130, 246, 0.12);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 6px;
    }
    
    /* Document card in sidebar */
    .doc-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Empty state hero */
    .empty-hero {
        background: rgba(255, 255, 255, 0.02);
        border: 1px dashed rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 40px 24px;
        text-align: center;
        margin: 20px 0;
    }
    .empty-hero-icon {
        font-size: 3rem;
        margin-bottom: 12px;
    }
    .empty-hero-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 8px;
    }
    .empty-hero-desc {
        color: #94a3b8;
        font-size: 0.95rem;
        max-width: 500px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)


def check_api_key_status() -> bool:
    """Check if GEMINI_API_KEY is configured properly."""
    try:
        return config.validate_config()
    except Exception:
        return False


def render_sidebar() -> int:
    """Render the sidebar with document upload, active document list, and settings.
    
    Returns:
        top_k: Number of chunks to retrieve for queries.
    """
    with st.sidebar:
        st.header("📚 Document Manager")
        
        # API Key health check
        has_key = check_api_key_status()
        if has_key:
            st.success("Gemini API Connected", icon="✅")
        else:
            st.error("Missing Gemini API Key", icon="⚠️")
            st.caption("Please configure `GEMINI_API_KEY` in `.env` to enable indexing and Q&A.")
            
        st.divider()

        # PDF Upload Section
        st.subheader("Upload PDF")
        uploaded_file = st.file_uploader(
            "Select a PDF document to index",
            type=["pdf"],
            help="Extracts text, creates Gemini embeddings, and stores in ChromaDB."
        )

        if uploaded_file is not None:
            upload_btn = st.button("Index Document", type="primary", use_container_width=True)
            if upload_btn:
                if not has_key:
                    st.error("Cannot index without a valid Gemini API key in `.env`.")
                else:
                    save_path = os.path.join(config.DOCUMENTS_DIR, uploaded_file.name)
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    with st.spinner(f"Indexing '{uploaded_file.name}' into vector database..."):
                        try:
                            num_chunks = ingest.ingest_pdf(save_path)
                            if num_chunks > 0:
                                st.success(f"Indexed **{num_chunks} chunks** from `{uploaded_file.name}`!")
                                st.rerun()
                            else:
                                st.warning("No readable text found in this PDF (may be image-only / scanned).")
                        except Exception as e:
                            st.error(f"Failed to index document: {str(e)}")

        st.divider()

        # Indexed Documents List
        st.subheader("Indexed Documents")
        try:
            indexed_docs = ingest.list_indexed_documents()
        except Exception:
            indexed_docs = []

        if indexed_docs:
            st.caption(f"Total documents: **{len(indexed_docs)}**")
            for doc_name in indexed_docs:
                col_name, col_del = st.columns([0.8, 0.2])
                with col_name:
                    st.write(f"📄 **{doc_name}**")
                with col_del:
                    if st.button("🗑️", key=f"del_{doc_name}", help=f"Delete {doc_name}"):
                        with st.spinner(f"Removing {doc_name}..."):
                            ingest.delete_document(doc_name)
                            # Remove file from disk if present
                            local_file = os.path.join(config.DOCUMENTS_DIR, doc_name)
                            if os.path.exists(local_file):
                                try:
                                    os.remove(local_file)
                                except Exception:
                                    pass
                            st.success(f"Deleted {doc_name}")
                            st.rerun()
        else:
            st.info("No documents indexed yet.")

        st.divider()

        # Search Settings
        st.subheader("Settings")
        top_k = st.slider(
            "Context Chunks (Top-K)",
            min_value=1,
            max_value=10,
            value=st.session_state.get("top_k", 4),
            help="Number of most similar text chunks to retrieve from ChromaDB."
        )
        st.session_state["top_k"] = top_k

        # Chat Management
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    return top_k


def render_citations(sources: List[Dict[str, Any]]):
    """Render citation chips for retrieved sources."""
    if not sources:
        return
    st.markdown("##### 📌 Citations:")
    chips_html = "".join([
        f'<span class="citation-chip">📄 {s.get("doc_name", "Doc")} &middot; Page {s.get("page", "?")}</span>'
        for s in sources
    ])
    st.markdown(chips_html, unsafe_allow_html=True)


def render_chunks_expander(chunks: List[Dict[str, Any]]):
    """Render expandable section showing retrieved passage details."""
    if not chunks:
        return
    with st.expander("🔍 View Retrieved Context Passages"):
        for i, chunk in enumerate(chunks, 1):
            doc = chunk.get("doc_name", "Unknown")
            page = chunk.get("page", "?")
            dist = chunk.get("distance", 0.0)
            st.markdown(f"**Chunk {i}** — *{doc} (Page {page})* | Distance: `{dist:.4f}`")
            st.text(chunk.get("text", ""))
            st.divider()


def main():
    """Main application loop."""
    # Initialize session state for chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Header section
    st.markdown('<div class="main-title">📚 Document-Grounded RAG Chatbot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Ask questions grounded strictly in your indexed PDF documents with verifiable citations.</div>',
        unsafe_allow_html=True
    )

    # Render sidebar controls
    top_k = render_sidebar()

    # Check for API key warning banner in main window
    has_key = check_api_key_status()
    if not has_key:
        st.warning(
            "⚠️ **Gemini API Key Required**: Add `GEMINI_API_KEY=your_key` to `.env` in the project root to enable embeddings and responses."
        )

    # Check indexed documents
    try:
        indexed_docs = ingest.list_indexed_documents()
    except Exception:
        indexed_docs = []

    # Display empty state hero when no documents are indexed
    if not indexed_docs and not st.session_state.messages:
        st.markdown("""
        <div class="empty-hero">
            <div class="empty-hero-icon">📄</div>
            <div class="empty-hero-title">No Documents Indexed</div>
            <div class="empty-hero-desc">
                Upload a PDF using the sidebar to start asking questions grounded in your document's text.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("role") == "assistant":
                if msg.get("sources"):
                    render_citations(msg["sources"])
                if msg.get("chunks"):
                    render_chunks_expander(msg["chunks"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Append and display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate answer with assistant
        with st.chat_message("assistant"):
            if not has_key:
                err_msg = "Please configure your `GEMINI_API_KEY` in the `.env` file to chat."
                st.error(err_msg)
                st.session_state.messages.append({"role": "assistant", "content": err_msg})
            elif not indexed_docs:
                info_msg = "No documents have been indexed yet. Please upload and index a PDF in the sidebar first."
                st.info(info_msg)
                st.session_state.messages.append({"role": "assistant", "content": info_msg})
            else:
                with st.spinner("Searching documents and generating grounded answer..."):
                    result = rag_pipeline.generate_answer(prompt, top_k=top_k)
                    answer = result.get("answer", "")
                    sources = result.get("sources", [])
                    chunks = result.get("retrieved_chunks", [])
                    is_refusal = result.get("is_refusal", False)

                    st.markdown(answer)

                    if sources and not is_refusal:
                        render_citations(sources)

                    if chunks:
                        render_chunks_expander(chunks)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources if not is_refusal else [],
                        "chunks": chunks,
                        "is_refusal": is_refusal
                    })


if __name__ == "__main__":
    main()
