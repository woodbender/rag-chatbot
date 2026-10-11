from typing import List, Dict, Any, Tuple
import config
import ingest

REFUSAL_MESSAGE = "I cannot answer this question based on the provided documents as the relevant information is not available."


def query_similar_chunks(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Retrieve top_k most similar document chunks from ChromaDB for a given query.

    Args:
        query: User question or search query string.
        top_k: Maximum number of chunks to retrieve.

    Returns:
        List of dicts containing 'id', 'text', 'doc_name', 'page', and 'distance'.
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    collection = ingest.get_chroma_collection()
    count = collection.count()
    if count == 0:
        return []

    n_results = min(top_k, count)
    query_vector = ingest.get_embedding(query.strip())

    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    chunks: List[Dict[str, Any]] = []
    if not results or not results.get("ids") or len(results["ids"]) == 0:
        return chunks

    ids = results["ids"][0]
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0] * len(ids)

    for i in range(len(ids)):
        meta = metas[i] if i < len(metas) and metas[i] else {}
        chunks.append({
            "id": ids[i],
            "text": docs[i] if i < len(docs) else "",
            "doc_name": meta.get("doc_name", "Unknown Document"),
            "page": meta.get("page", 1),
            "distance": float(distances[i]) if i < len(distances) else 0.0
        })

    return chunks


def format_context(chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
    """Format retrieved document chunks into context string with citations.

    Args:
        chunks: List of retrieved chunk dictionaries.

    Returns:
        Tuple of (formatted_context_string, deduplicated_sources_list).
    """
    if not chunks:
        return "", []

    context_segments = []
    sources_set = set()

    for chunk in chunks:
        doc_name = chunk.get("doc_name", "Unknown Document")
        page = chunk.get("page", 1)
        text = chunk.get("text", "").strip()

        context_segments.append(f"[Document: {doc_name}, Page: {page}]\n{text}")
        sources_set.add((doc_name, page))

    formatted_context = "\n\n".join(context_segments)
    deduplicated_sources = [
        {"doc_name": doc, "page": page}
        for doc, page in sorted(list(sources_set), key=lambda x: (x[0], x[1]))
    ]

    return formatted_context, deduplicated_sources


def build_rag_prompt(query: str, context: str) -> str:
    """Construct a grounded prompt combining system instructions, document context, and user query.

    Args:
        query: User question string.
        context: Formatted document context string.

    Returns:
        Structured prompt string.
    """
    return f"""You are a helpful and precise document-grounded assistant. Answer the user's question using ONLY the provided document context below.

CRITICAL INSTRUCTIONS:
1. Grounding: Answer strictly using facts directly stated in the context below. Do NOT use any external knowledge, assumptions, or extrapolations.
2. Citations: For every factual claim in your answer, provide the source citation in the format [Doc: <doc_name>, Page: <page>].
3. Anti-Hallucination Fallback: If the provided context is empty, does not contain the answer, or does not provide sufficient information to answer the question with certainty, you MUST respond EXACTLY with:
"{REFUSAL_MESSAGE}"
Do not attempt to provide a partial guess or hallucinated answer.

---
DOCUMENT CONTEXT:
{context}
---

USER QUESTION:
{query}

ANSWER:"""


def call_gemini_model(prompt: str) -> str:
    """Call Google Gemini model to generate a text response.

    Args:
        prompt: Formatted prompt string.

    Returns:
        Generated response text string.
    """
    client = ingest.get_genai_client()
    response = client.models.generate_content(
        model=config.CHAT_MODEL,
        contents=prompt
    )
    if not response or not response.text:
        return REFUSAL_MESSAGE
    return response.text.strip()


def is_refusal_response(answer: str) -> bool:
    """Check if the generated response represents a refusal or unanswerable outcome.

    Args:
        answer: Response text string.

    Returns:
        True if answer is a refusal.
    """
    if not answer:
        return True
    lower = answer.lower()
    if REFUSAL_MESSAGE.lower() in lower:
        return True
    refusal_indicators = [
        "cannot answer this question based on the provided documents",
        "provided documents do not contain",
        "relevant information is not available",
        "no documents have been indexed yet",
        "information is not provided in the document",
        "not mentioned in the context",
    ]
    return any(indicator in lower for indicator in refusal_indicators)


def generate_answer(query: str, top_k: int = 4) -> Dict[str, Any]:
    """Execute end-to-end RAG pipeline: retrieval, context assembly, grounding generation, and fallback.

    Args:
        query: User question string.
        top_k: Number of nearest chunks to retrieve.

    Returns:
        Dict with keys:
          - 'answer': text response
          - 'sources': list of unique citation dicts [{'doc_name': ..., 'page': ...}]
          - 'retrieved_chunks': list of raw retrieved chunk dicts
          - 'is_refusal': boolean flag
    """
    if not query or not query.strip():
        return {
            "answer": "Please enter a valid question.",
            "sources": [],
            "retrieved_chunks": [],
            "is_refusal": True
        }

    # Verify if collection has documents
    try:
        collection = ingest.get_chroma_collection()
        if collection.count() == 0:
            return {
                "answer": "No documents have been indexed yet. Please upload and index a PDF first.",
                "sources": [],
                "retrieved_chunks": [],
                "is_refusal": True
            }
    except Exception as e:
        return {
            "answer": f"Error accessing vector database: {str(e)}",
            "sources": [],
            "retrieved_chunks": [],
            "is_refusal": True
        }

    # Retrieve similar chunks
    try:
        chunks = query_similar_chunks(query, top_k=top_k)
    except Exception as e:
        return {
            "answer": f"Error retrieving document chunks: {str(e)}",
            "sources": [],
            "retrieved_chunks": [],
            "is_refusal": True
        }

    if not chunks:
        return {
            "answer": REFUSAL_MESSAGE,
            "sources": [],
            "retrieved_chunks": [],
            "is_refusal": True
        }

    context, sources = format_context(chunks)
    prompt = build_rag_prompt(query, context)

    # Call Gemini model
    try:
        raw_answer = call_gemini_model(prompt)
        refusal = is_refusal_response(raw_answer)
        return {
            "answer": raw_answer,
            "sources": sources if not refusal else [],
            "retrieved_chunks": chunks,
            "is_refusal": refusal
        }
    except Exception as e:
        return {
            "answer": f"Error generating answer with Gemini: {str(e)}",
            "sources": [],
            "retrieved_chunks": chunks,
            "is_refusal": True
        }
