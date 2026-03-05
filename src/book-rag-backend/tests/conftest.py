import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import Request

from book_rag_backend.app import app
from book_rag_backend.config import Config


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client(mock_config):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    from book_rag_backend.app import app
    
    # Override the app state for testing
    app.state.qdrant_client = AsyncMock()
    app.state.embedding_model = AsyncMock()
    app.state.config = mock_config
    
    return TestClient(app)


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = MagicMock(spec=Config)
    config.qdrant.collection_name = "test_collection"
    config.qdrant.url = "http://localhost:6333"
    config.qdrant.api_key = "test_api_key"
    config.splitter.chunk_size = 1000
    config.splitter.chunk_overlap = 200
    config.model.url = "http://localhost:11434"
    config.model.api_key = "test_llm_api_key"
    config.model.model = "llama2"
    return config


@pytest.fixture
def mock_request(mock_config):
    """Create a mock FastAPI Request object."""
    request = MagicMock(spec=Request)
    request.app = MagicMock()
    request.app.state = MagicMock()
    request.app.state.config = mock_config
    request.app.state.qdrant_client = AsyncMock()
    request.app.state.embedding_model = AsyncMock()
    return request


@pytest.fixture
def sample_book_id():
    """Generate a sample UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_pdf_content():
    """Create sample PDF content for testing."""
    return b"Sample PDF content for testing purposes."


@pytest.fixture
def sample_text_content():
    """Create sample text content for testing."""
    return "This is a sample book content for testing purposes. " * 100


@pytest.fixture
def sample_chunks():
    """Create sample text chunks for testing."""
    return [
        "This is the first chunk of the book content.",
        "This is the second chunk of the book content.",
        "This is the third chunk of the book content.",
    ]


@pytest.fixture
def sample_vectors():
    """Create sample embedding vectors for testing."""
    return [
        [0.1, 0.2, 0.3, 0.4, 0.5] * 76,  # 380-dimensional vector
        [0.2, 0.3, 0.4, 0.5, 0.6] * 76,
        [0.3, 0.4, 0.5, 0.6, 0.7] * 76,
    ]


@pytest.fixture
def sample_messages():
    """Create sample chat messages for testing."""
    return [
        {"role": "user", "content": "What is this book about?"},
        {"role": "assistant", "content": "This is a sample book for testing."},
        {"role": "user", "content": "Tell me more about the main topic."},
    ]
