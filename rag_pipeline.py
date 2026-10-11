from typing import List, Dict, Any, Tuple
import config
import ingest


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
