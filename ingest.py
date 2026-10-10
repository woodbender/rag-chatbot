import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf
import chromadb
from google import genai

import config


def get_genai_client() -> genai.Client:
    """Initialize and return Google GenAI Client using configured API key.

    Returns:
        genai.Client instance.
    """
    config.validate_config()
    return genai.Client(api_key=config.GEMINI_API_KEY)


def get_chroma_collection() -> chromadb.api.models.Collection.Collection:
    """Get or create the ChromaDB persistent collection.

    Returns:
        ChromaDB Collection instance.
    """
    os.makedirs(config.CHROMA_DB_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
    return chroma_client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def get_embedding(text: str) -> List[float]:
    """Generate vector embedding for a single text string using Gemini API.

    Args:
        text: Input text string to embed.

    Returns:
        List of floats representing the embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate embedding for empty text.")

    client = get_genai_client()
    response = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=text.strip()
    )
    if not response.embeddings or len(response.embeddings) == 0:
        raise RuntimeError("Gemini embedding API returned empty response.")
    return list(response.embeddings[0].values)


def get_embeddings_batch(texts: List[str], batch_size: int = 16) -> List[List[float]]:
    """Generate vector embeddings for a list of text strings in batches.

    Args:
        texts: List of text strings.
        batch_size: Batch size for Gemini API request.

    Returns:
        List of embedding vectors.
    """
    if not texts:
        return []

    client = get_genai_client()
    all_embeddings: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = [t.strip() for t in texts[i:i + batch_size]]
        response = client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=batch
        )
        if not response.embeddings:
            raise RuntimeError(f"Gemini embedding API returned empty embeddings for batch starting at index {i}.")
        all_embeddings.extend([list(emb.values) for emb in response.embeddings])

    return all_embeddings


def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extract page-level text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        List of dicts containing 'page' (1-indexed) and 'text' string.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at path: {pdf_path}")

    pages_data = []
    try:
        doc = pymupdf.open(pdf_path)
        for page_idx, page in enumerate(doc):
            text = page.get_text("text").strip()
            pages_data.append({
                "page": page_idx + 1,
                "text": text
            })
        doc.close()
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF '{pdf_path}': {str(e)}")

    return pages_data


def chunk_text(
    pages_data: List[Dict[str, Any]],
    doc_name: str,
    chunk_size: int = config.CHUNK_SIZE,
    overlap: int = config.CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """Split extracted page text into overlapping text chunks.

    Args:
        pages_data: List of dicts with 'page' and 'text'.
        doc_name: Basename of the source document.
        chunk_size: Maximum character count per chunk.
        overlap: Character overlap between consecutive chunks.

    Returns:
        List of chunk dicts containing 'id', 'text', 'doc_name', and 'page'.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be strictly less than chunk_size.")

    chunks = []
    step = chunk_size - overlap
    chunk_counter = 0

    for item in pages_data:
        page_num = item["page"]
        text = item["text"]

        if not text:
            continue

        if len(text) <= chunk_size:
            chunk_counter += 1
            chunks.append({
                "id": f"{doc_name}_p{page_num}_c{chunk_counter}",
                "text": text,
                "doc_name": doc_name,
                "page": page_num
            })
            continue

        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_str = text[start:end].strip()

            if chunk_str:
                chunk_counter += 1
                chunks.append({
                    "id": f"{doc_name}_p{page_num}_c{chunk_counter}",
                    "text": chunk_str,
                    "doc_name": doc_name,
                    "page": page_num
                })

            start += step

    return chunks


def delete_document(doc_name: str) -> None:
    """Delete all indexed chunks associated with doc_name from ChromaDB collection.

    Args:
        doc_name: Basename of document to remove.
    """
    collection = get_chroma_collection()
    collection.delete(where={"doc_name": doc_name})


def list_indexed_documents() -> List[str]:
    """Retrieve list of unique document names currently stored in ChromaDB.

    Returns:
        List of unique document name strings.
    """
    collection = get_chroma_collection()
    results = collection.get(include=["metadatas"])
    if not results or not results.get("metadatas"):
        return []

    doc_names = set()
    for meta in results["metadatas"]:
        if meta and "doc_name" in meta:
            doc_names.add(meta["doc_name"])

    return sorted(list(doc_names))


def ingest_pdf(pdf_path: str) -> int:
    """Ingest a PDF file into ChromaDB vector database.

    Extracts text, splits into chunks, generates Gemini embeddings,
    and persists chunks to ChromaDB collection. Existing chunks for
    the document are replaced.

    Args:
        pdf_path: Path to the target PDF file.

    Returns:
        Number of chunks successfully indexed.
    """
    doc_name = os.path.basename(pdf_path)
    pages_data = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(pages_data, doc_name=doc_name)

    if not chunks:
        return 0

    # Delete existing entries for doc_name to avoid duplicates
    delete_document(doc_name)

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [{"doc_name": c["doc_name"], "page": c["page"]} for c in chunks]

    embeddings = get_embeddings_batch(texts)

    collection = get_chroma_collection()
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    return len(chunks)
