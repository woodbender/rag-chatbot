import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf

import config


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
            # Retain page entry even if empty (for page numbering accuracy)
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

        # If page text is shorter than chunk size, create a single chunk
        if len(text) <= chunk_size:
            chunk_counter += 1
            chunks.append({
                "id": f"{doc_name}_p{page_num}_c{chunk_counter}",
                "text": text,
                "doc_name": doc_name,
                "page": page_num
            })
            continue

        # Sliding window chunking
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
