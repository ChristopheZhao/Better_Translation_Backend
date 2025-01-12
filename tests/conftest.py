import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.config import get_settings

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_settings():
    return get_settings()

@pytest.fixture
def sample_texts():
    return {
        "short": "Hello, this is a test message.",
        "medium": """
        This is a test paragraph. It contains multiple sentences.
        Let's see how the translation works with longer texts.
        We want to test both the chunking and translation quality.
        """,
        "long": """
        In this comprehensive test, we'll examine several aspects of our translation system.
        First, we need to ensure that sentence boundaries are properly detected.
        Then, we'll verify that the chunking mechanism works correctly with longer texts.
        Finally, we'll check if the translation maintains proper formatting and structure.
        
        This is a new paragraph. It should be handled separately.
        The system should preserve the paragraph breaks and formatting.
        """
    }