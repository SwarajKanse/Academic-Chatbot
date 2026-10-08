import pytest
from rag_engine import DocumentChunk, AcademicRAGEngine
from sklearn.feature_extraction.text import TfidfVectorizer


def test_document_chunk_structure():
    chunk = DocumentChunk(text="Quantum mechanics is a fundamental theory in physics.", source="quantum.pdf", page=5, chunk_id=12)
    assert chunk.text == "Quantum mechanics is a fundamental theory in physics."
    assert chunk.source == "quantum.pdf"
    assert chunk.page == 5
    assert chunk.chunk_id == 12
    d = chunk.to_dict()
    assert d["source"] == "quantum.pdf"
    assert d["page"] == 5
    assert d["chunk_id"] == 12


def test_academic_rag_chunking():
    engine = AcademicRAGEngine()
    long_text = "Section 1: Data Structures and Algorithms. " * 50
    chunks = engine._chunk_text(long_text, max_chars=200, overlap=40)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) > 0


def test_academic_rag_vector_search(mock_document_chunks):
    engine = AcademicRAGEngine()
    engine.chunks = mock_document_chunks
    texts = [c.text for c in engine.chunks]
    engine.vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    engine.tfidf_matrix = engine.vectorizer.fit_transform(texts)

    results = engine.retrieve("continuous change and differentiation", top_k=2)
    assert len(results) > 0
    assert "calculus" in results[0][0].text.lower()


def test_strict_grounded_refusal_detection():
    engine = AcademicRAGEngine()
    # Empty chunks in strict mode must refuse
    engine.chunks = []
    events = list(engine.generate_answer_stream(
        query="What is the capital of France?",
        history=[],
        strict_mode=True
    ))
    combined_response = "".join(
        ev.get("content", "") if isinstance(ev, dict) else str(ev)
        for ev, _ in events
    )
    assert "No documents uploaded" in combined_response or "Strict RAG" in combined_response
