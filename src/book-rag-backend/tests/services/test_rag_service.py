import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from book_rag_backend.services.rag import RAGService
from tests.mocks.mock_services import (
    MockQdrantService,
    MockEmbeddingsService,
    MockLLMService
)


@pytest.fixture
def rag_service():
    """Create a RAGService instance with mock dependencies."""
    return RAGService(
        qdrant=MockQdrantService(),
        embeddings=MockEmbeddingsService(),
        llm=MockLLMService("http://localhost:11434", "test_key", "llama2"),
        top_k=3,
        score_threshold=0.8,
        max_context_tokens=1000
    )


@pytest.fixture
def sample_book_id():
    """Generate a sample UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_messages():
    """Create sample chat messages for testing."""
    return [
        {"role": "user", "content": "What is this book about?"},
        {"role": "assistant", "content": "This is a sample book for testing."},
        {"role": "user", "content": "Tell me more about the main topic."},
    ]


@pytest.fixture
def sample_chunks():
    """Create sample search chunks for testing."""
    return [
        {"id": "chunk1", "content": "This is the first relevant chunk from the book.", "score": 0.9},
        {"id": "chunk2", "content": "This is the second relevant chunk from the book.", "score": 0.85},
        {"id": "chunk3", "content": "This is the third relevant chunk from the book.", "score": 0.8},
    ]


class TestRAGService:
    """Test cases for RAGService."""

    def test_init_default_values(self):
        """Test RAGService initialization with default values."""
        mock_qdrant = MagicMock()
        mock_embeddings = MagicMock()
        mock_llm = MagicMock()
        
        service = RAGService(
            qdrant=mock_qdrant,
            embeddings=mock_embeddings,
            llm=mock_llm
        )
        
        assert service.qdrant is mock_qdrant
        assert service.embeddings is mock_embeddings
        assert service.llm is mock_llm
        assert service.top_k == 5
        assert service.score_threshold == 0.7
        assert service.max_context_tokens == 200000

    def test_init_custom_values(self):
        """Test RAGService initialization with custom values."""
        mock_qdrant = MagicMock()
        mock_embeddings = MagicMock()
        mock_llm = MagicMock()
        
        service = RAGService(
            qdrant=mock_qdrant,
            embeddings=mock_embeddings,
            llm=mock_llm,
            top_k=10,
            score_threshold=0.5,
            max_context_tokens=5000
        )
        
        assert service.top_k == 10
        assert service.score_threshold == 0.5
        assert service.max_context_tokens == 5000

    @pytest.mark.asyncio
    async def test_search_in_book_success(self, rag_service, sample_book_id, sample_messages, sample_chunks):
        """Test successful search in book."""
        # Mock the dependencies
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=sample_chunks)
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="This is the RAG-generated answer.")
        
        result = await rag_service.search_in_book(sample_book_id, sample_messages)
        
        # Verify the result contains the assistant's response
        assert len(result) == len(sample_messages) + 1
        assert result[-1]["role"] == "assistant"
        assert result[-1]["content"] == "This is the RAG-generated answer."
        
        # Verify the original messages are preserved
        assert result[:-1] == sample_messages
        
        # Verify method calls
        rag_service.qdrant.book_exists.assert_called_once_with(sample_book_id)
        rag_service.embeddings.embed.assert_called_once_with("Tell me more about the main topic.")
        rag_service.qdrant.semantic_search_in_book.assert_called_once_with(
            book_id=sample_book_id,
            query_vector=[0.1, 0.2, 0.3],
            limit=rag_service.top_k,
            score_threshold=rag_service.score_threshold
        )
        rag_service.llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_in_book_not_found(self, rag_service, sample_book_id, sample_messages):
        """Test search in book when book doesn't exist."""
        mock_book_exists = AsyncMock(return_value=False)
        rag_service.qdrant.book_exists = mock_book_exists
        
        with pytest.raises(ValueError, match="NotFound"):
            await rag_service.search_in_book(sample_book_id, sample_messages)
        
        mock_book_exists.assert_called_once_with(sample_book_id)

    @pytest.mark.asyncio
    async def test_search_in_book_empty_chunks(self, rag_service, sample_book_id, sample_messages):
        """Test search in book when no relevant chunks found."""
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[])
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="I don't have enough information to answer this question.")
        
        result = await rag_service.search_in_book(sample_book_id, sample_messages)
        
        # Should still return a response even with empty chunks
        assert len(result) == len(sample_messages) + 1
        assert result[-1]["role"] == "assistant"
        
        # Verify the context is empty
        llm_call_args = rag_service.llm.generate.call_args[0][0]
        llm_messages = llm_call_args
        user_message = llm_messages[-1]["content"]
        assert "Контекст из книги:\n\n" in user_message  # Empty context

    @pytest.mark.asyncio
    async def test_search_in_book_single_message(self, rag_service, sample_book_id):
        """Test search in book with only one user message."""
        single_message = [{"role": "user", "content": "What is this book about?"}]
        
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[
            {"content": "This is a book about testing.", "score": 0.9}
        ])
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="This book is about testing.")
        
        result = await rag_service.search_in_book(sample_book_id, single_message)
        
        assert len(result) == 2
        assert result[0] == single_message[0]
        assert result[1]["role"] == "assistant"
        
        # Verify the question extraction works correctly
        rag_service.embeddings.embed.assert_called_once_with("What is this book about?")

    @pytest.mark.asyncio
    async def test_search_in_book_context_formation(self, rag_service, sample_book_id, sample_messages, sample_chunks):
        """Test that context is formed correctly from chunks."""
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=sample_chunks)
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="Answer based on context.")
        
        await rag_service.search_in_book(sample_book_id, sample_messages)
        
        # Get the LLM call arguments
        llm_call_args = rag_service.llm.generate.call_args[0][0]
        llm_messages = llm_call_args
        user_message = llm_messages[-1]["content"]
        
        # Verify context format
        expected_context = (
            "[Источник 1]: This is the first relevant chunk from the book.\n\n"
            "[Источник 2]: This is the second relevant chunk from the book.\n\n"
            "[Источник 3]: This is the third relevant chunk from the book."
        )
        assert f"Контекст из книги:\n{expected_context}" in user_message
        assert "Вопрос пользователя: Tell me more about the main topic." in user_message

    @pytest.mark.asyncio
    async def test_search_in_book_system_prompt(self, rag_service, sample_book_id, sample_messages):
        """Test that system prompt is correctly included."""
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[])
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="Answer.")
        
        await rag_service.search_in_book(sample_book_id, sample_messages)
        
        # Get the LLM call arguments
        llm_call_args = rag_service.llm.generate.call_args[0][0]
        llm_messages = llm_call_args
        
        # Verify system prompt
        assert llm_messages[0]["role"] == "system"
        assert "полезный ассистент" in llm_messages[0]["content"]
        assert "используй только предоставленные источники" in llm_messages[0]["content"].lower()

    @pytest.mark.asyncio
    async def test_search_in_book_message_history_preservation(self, rag_service, sample_book_id, sample_messages):
        """Test that message history is correctly preserved."""
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[])
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(return_value="Answer.")
        
        result = await rag_service.search_in_book(sample_book_id, sample_messages)
        
        # Get the LLM call arguments
        llm_call_args = rag_service.llm.generate.call_args[0][0]
        llm_messages = llm_call_args
        
        # Verify that all original messages (except last user message) are included
        assert len(llm_messages) == 4  # system + 2 original messages + augmented question
        assert llm_messages[1]["role"] == "user"
        assert llm_messages[1]["content"] == "What is this book about?"
        assert llm_messages[2]["role"] == "assistant"
        assert llm_messages[2]["content"] == "This is a sample book for testing."

    @pytest.mark.asyncio
    async def test_search_in_book_embeddings_error(self, rag_service, sample_book_id, sample_messages):
        """Test search in book when embeddings service fails."""
        mock_book_exists = AsyncMock(return_value=True)
        mock_embed = MagicMock(side_effect=Exception("Embedding error"))
        
        rag_service.qdrant.book_exists = mock_book_exists
        rag_service.embeddings.embed = mock_embed
        
        with pytest.raises(Exception, match="Embedding error"):
            await rag_service.search_in_book(sample_book_id, sample_messages)
        
        mock_book_exists.assert_called_once_with(sample_book_id)
        mock_embed.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_in_book_qdrant_search_error(self, rag_service, sample_book_id, sample_messages):
        """Test search in book when Qdrant search fails."""
        mock_book_exists = AsyncMock(return_value=True)
        mock_embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        mock_search = AsyncMock(side_effect=Exception("Search error"))
        
        rag_service.qdrant.book_exists = mock_book_exists
        rag_service.embeddings.embed = mock_embed
        rag_service.qdrant.semantic_search_in_book = mock_search
        
        with pytest.raises(Exception, match="Search error"):
            await rag_service.search_in_book(sample_book_id, sample_messages)
        
        mock_book_exists.assert_called_once_with(sample_book_id)
        mock_embed.assert_called_once()
        mock_search.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_in_book_llm_error(self, rag_service, sample_book_id, sample_messages):
        """Test search in book when LLM generation fails."""
        rag_service.qdrant.book_exists = AsyncMock(return_value=True)
        rag_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[])
        rag_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        rag_service.llm.generate = AsyncMock(side_effect=Exception("LLM error"))
        
        with pytest.raises(Exception, match="LLM error"):
            await rag_service.search_in_book(sample_book_id, sample_messages)
        
        rag_service.qdrant.book_exists.assert_called_once_with(sample_book_id)
        rag_service.embeddings.embed.assert_called_once()
        rag_service.qdrant.semantic_search_in_book.assert_called_once()
        rag_service.llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_in_book_custom_parameters(self, sample_book_id, sample_messages):
        """Test search in book with custom RAG parameters."""
        custom_service = RAGService(
            qdrant=MockQdrantService(),
            embeddings=MockEmbeddingsService(),
            llm=MockLLMService("http://localhost:11434", "test_key", "llama2"),
            top_k=10,
            score_threshold=0.5,
            max_context_tokens=5000
        )
        
        custom_service.qdrant.book_exists = AsyncMock(return_value=True)
        custom_service.qdrant.semantic_search_in_book = AsyncMock(return_value=[])
        custom_service.embeddings.embed = MagicMock(return_value=[0.1, 0.2, 0.3])
        custom_service.llm.generate = AsyncMock(return_value="Answer.")
        
        await custom_service.search_in_book(sample_book_id, sample_messages)
        
        # Verify custom parameters are used
        custom_service.qdrant.semantic_search_in_book.assert_called_once_with(
            book_id=sample_book_id,
            query_vector=[0.1, 0.2, 0.3],
            limit=10,
            score_threshold=0.5
        )
