import os
import unittest
from unittest.mock import patch, MagicMock

import config
import ingest
import rag_pipeline
import app


class TestConfiguration(unittest.TestCase):
    """Test configuration module values and validation logic."""

    def test_constants_defined(self):
        self.assertTrue(hasattr(config, "CHROMA_DB_DIR"))
        self.assertTrue(hasattr(config, "DOCUMENTS_DIR"))
        self.assertEqual(config.EMBEDDING_MODEL, "gemini-embedding-001")
        self.assertEqual(config.CHAT_MODEL, "gemini-2.5-flash")
        self.assertGreater(config.CHUNK_SIZE, 0)
        self.assertGreater(config.CHUNK_OVERLAP, 0)
        self.assertLess(config.CHUNK_OVERLAP, config.CHUNK_SIZE)

    def test_validate_config_missing_key(self):
        with patch.object(config, "GEMINI_API_KEY", ""):
            with self.assertRaises(ValueError):
                config.validate_config()

        with patch.object(config, "GEMINI_API_KEY", "your_gemini_api_key_here"):
            with self.assertRaises(ValueError):
                config.validate_config()

    def test_validate_config_valid_key(self):
        with patch.object(config, "GEMINI_API_KEY", "valid_test_api_key_123"):
            self.assertTrue(config.validate_config())
            self.assertTrue(os.path.exists(config.CHROMA_DB_DIR))
            self.assertTrue(os.path.exists(config.DOCUMENTS_DIR))


class TestIngestion(unittest.TestCase):
    """Test PDF text extraction, chunking, and metadata retention."""

    def test_extract_text_from_existing_pdf(self):
        sample_pdf = os.path.join(config.DOCUMENTS_DIR, "test_sample.pdf")
        if os.path.exists(sample_pdf):
            pages = ingest.extract_text_from_pdf(sample_pdf)
            self.assertIsInstance(pages, list)
            self.assertGreater(len(pages), 0)
            self.assertEqual(pages[0]["page"], 1)
            self.assertIn("RAG chatbot", pages[0]["text"])

    def test_extract_text_from_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            ingest.extract_text_from_pdf("non_existent_file.pdf")

    def test_chunk_text_generation(self):
        pages_data = [
            {"page": 1, "text": "A" * 1500},
            {"page": 2, "text": "B" * 500}
        ]
        chunks = ingest.chunk_text(pages_data, doc_name="test.pdf", chunk_size=1000, overlap=200)
        self.assertGreater(len(chunks), 1)

        # Verify chunk structure
        for chunk in chunks:
            self.assertIn("id", chunk)
            self.assertIn("text", chunk)
            self.assertEqual(chunk["doc_name"], "test.pdf")
            self.assertIn(chunk["page"], [1, 2])
            self.assertTrue(chunk["id"].startswith("test.pdf_p"))

    def test_chunk_text_invalid_params(self):
        with self.assertRaises(ValueError):
            ingest.chunk_text([], "doc.pdf", chunk_size=-1)
        with self.assertRaises(ValueError):
            ingest.chunk_text([], "doc.pdf", chunk_size=100, overlap=100)


class TestVectorStoreOperations(unittest.TestCase):
    """Test ChromaDB collection interactions, indexing, and deletion."""

    def setUp(self):
        import chromadb
        self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_DIR)
        self.test_col = self.chroma_client.get_or_create_collection(
            name="test_temp_collection",
            metadata={"hnsw:space": "cosine"}
        )

    def tearDown(self):
        try:
            self.chroma_client.delete_collection("test_temp_collection")
        except Exception:
            pass

    def test_add_query_and_delete_in_collection(self):
        # Add test vectors with distinct orthogonal directions
        vec_a = [1.0] + [0.0] * 767
        vec_b = [0.0] + [1.0] + [0.0] * 766
        self.test_col.add(
            ids=["docA_p1_c1", "docB_p1_c1"],
            embeddings=[vec_a, vec_b],
            documents=["Sample text from Document A", "Sample text from Document B"],
            metadatas=[{"doc_name": "docA.pdf", "page": 1}, {"doc_name": "docB.pdf", "page": 1}]
        )
        self.assertEqual(self.test_col.count(), 2)

        # Query with vec_a
        res = self.test_col.query(
            query_embeddings=[vec_a],
            n_results=1
        )
        self.assertEqual(res["ids"][0][0], "docA_p1_c1")
        self.assertEqual(res["metadatas"][0][0]["doc_name"], "docA.pdf")

        # Delete document A
        self.test_col.delete(where={"doc_name": "docA.pdf"})
        self.assertEqual(self.test_col.count(), 1)
        remaining = self.test_col.get()
        self.assertEqual(remaining["ids"][0], "docB_p1_c1")


class TestRAGPipeline(unittest.TestCase):
    """Test similarity search formatting, prompt engineering, and guardrails."""

    def test_format_context_empty(self):
        ctx, sources = rag_pipeline.format_context([])
        self.assertEqual(ctx, "")
        self.assertEqual(sources, [])

    def test_format_context_with_citations(self):
        chunks = [
            {"doc_name": "guide.pdf", "page": 2, "text": "Content snippet 1"},
            {"doc_name": "guide.pdf", "page": 2, "text": "Content snippet 2"},
            {"doc_name": "manual.pdf", "page": 5, "text": "Content snippet 3"}
        ]
        ctx, sources = rag_pipeline.format_context(chunks)
        self.assertIn("[Document: guide.pdf, Page: 2]", ctx)
        self.assertIn("[Document: manual.pdf, Page: 5]", ctx)
        # Deduplication check: 2 unique (doc, page) pairs
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0]["doc_name"], "guide.pdf")
        self.assertEqual(sources[1]["doc_name"], "manual.pdf")

    def test_build_rag_prompt_structure(self):
        prompt = rag_pipeline.build_rag_prompt(
            query="What is the operating voltage?",
            context="[Document: specs.pdf, Page: 1]\nOperating voltage is 24V DC."
        )
        self.assertIn("CRITICAL INSTRUCTIONS", prompt)
        self.assertIn(rag_pipeline.REFUSAL_MESSAGE, prompt)
        self.assertIn("Operating voltage is 24V DC", prompt)
        self.assertIn("What is the operating voltage?", prompt)

    def test_is_refusal_response(self):
        # Exact refusal
        self.assertTrue(rag_pipeline.is_refusal_response(rag_pipeline.REFUSAL_MESSAGE))
        # Variants
        self.assertTrue(rag_pipeline.is_refusal_response(
            "I cannot answer this question based on the provided documents."
        ))
        self.assertTrue(rag_pipeline.is_refusal_response(
            "The provided documents do not contain information about this query."
        ))
        self.assertTrue(rag_pipeline.is_refusal_response(
            "This information is not provided in the document."
        ))
        # Valid answer with source citation
        self.assertFalse(rag_pipeline.is_refusal_response(
            "According to [Doc: specs.pdf, Page: 1], the operating voltage is 24V DC."
        ))

    def test_generate_answer_empty_query(self):
        result = rag_pipeline.generate_answer("")
        self.assertTrue(result["is_refusal"])
        self.assertIn("valid question", result["answer"])
        self.assertEqual(result["sources"], [])

    def test_generate_answer_empty_database(self):
        mock_col = MagicMock()
        mock_col.count.return_value = 0
        with patch("ingest.get_chroma_collection", return_value=mock_col):
            result = rag_pipeline.generate_answer("Any question?")
            self.assertTrue(result["is_refusal"])
            self.assertIn("No documents have been indexed yet", result["answer"])
            self.assertEqual(result["sources"], [])


class TestAppModule(unittest.TestCase):
    """Test Streamlit application helpers and component logic."""

    def test_check_api_key_status(self):
        with patch("config.validate_config", return_value=True):
            self.assertTrue(app.check_api_key_status())

        with patch("config.validate_config", side_effect=ValueError("Missing")):
            self.assertFalse(app.check_api_key_status())


if __name__ == "__main__":
    unittest.main()
