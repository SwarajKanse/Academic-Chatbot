import pytest
import os
import sys

# Ensure project root is in python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Ensure mock key exists for testing in isolated CI/CD environments
os.environ.setdefault("GROQ_API_KEY", "gsk_mock_ci_test_key_00000000000000000000")


@pytest.fixture
def sample_academic_text():
    return (
        "Linear algebra is the branch of mathematics concerning linear equations such as "
        "a1*x1 + ... + an*xn = b, linear maps, and their representations in vector spaces "
        "through matrices. Eigenvalues and eigenvectors are fundamental in matrix diagonalization."
    )


@pytest.fixture
def mock_document_chunks():
    from rag_engine import DocumentChunk
    return [
        DocumentChunk(
            text="Calculus is the mathematical study of continuous change, in the same way that geometry is the study of shape.",
            source="calculus_ch1.pdf",
            page=1,
            chunk_id=0
        ),
        DocumentChunk(
            text="The fundamental theorem of calculus connects differentiation and integration.",
            source="calculus_ch1.pdf",
            page=2,
            chunk_id=1
        )
    ]
