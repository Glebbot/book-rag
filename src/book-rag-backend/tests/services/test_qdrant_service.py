import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from book_rag_backend.services.qdrant import QdrantService


@pytest.fixture
def mock_qdrant_client():
    """Create a mock Qdrant client."""
    return AsyncMock()


@pytest.fixture
def qdrant_service(mock_qdrant_client):
    """Create a QdrantService instance with mock client."""
    return QdrantService(client=mock_qdrant_client, collection="test_collection")


@pytest.fixture
def sample_book_id():
    """Generate a sample UUID for testing."""
    return uuid4()


@pytest.fixture
def sample_points():
    """Create sample points for testing."""
    return [
        MagicMock(
            id="point1",
            payload={
                "content": "This is the first chunk content.",
                "book_id": "book1",
                "name": "Test Book",
                "author": "Test Author"
            }
        ),
        MagicMock(
            id="point2", 
            payload={
                "content": "This is the second chunk content.",
                "book_id": "book1",
                "name": "Test Book",
                "author": "Test Author"
            }
        )
    ]


@pytest.fixture
def sample_search_results():
    """Create sample search results for testing."""
    mock_point1 = MagicMock()
    mock_point1.payload = {
        "content": "Relevant content 1",
        "book_id": "book1",
        "name": "Test Book"
    }
    
    mock_point2 = MagicMock()
    mock_point2.payload = {
        "content": "Relevant content 2", 
        "book_id": "book1",
        "author": "Test Author"
    }
    
    mock_results = MagicMock()
    mock_results.points = [mock_point1, mock_point2]
    return mock_results


class TestQdrantService:
    """Test cases for QdrantService."""

    def test_init(self):
        """Test QdrantService initialization."""
        mock_client = MagicMock()
        service = QdrantService(client=mock_client, collection="test_collection")
        
        assert service.client is mock_client
        assert service.collection == "test_collection"

    @pytest.mark.asyncio
    async def test_delete_book_success(self, qdrant_service, sample_book_id):
        """Test successful book deletion."""
        # Mock count result to show book exists
        mock_count_result = MagicMock()
        mock_count_result.count = 5
        qdrant_service.client.count.return_value = mock_count_result
        
        await qdrant_service.delete_book(sample_book_id)
        
        # Verify count was called with correct filter
        qdrant_service.client.count.assert_called_once()
        call_args = qdrant_service.client.count.call_args
        assert call_args[1]["collection_name"] == "test_collection"
        
        # Verify delete was called
        qdrant_service.client.delete.assert_called_once()
        delete_args = qdrant_service.client.delete.call_args
        assert delete_args[1]["collection_name"] == "test_collection"
        assert delete_args[1]["wait"] is True

    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, qdrant_service, sample_book_id):
        """Test book deletion when book doesn't exist."""
        # Mock count result to show book doesn't exist
        mock_count_result = MagicMock()
        mock_count_result.count = 0
        qdrant_service.client.count.return_value = mock_count_result
        
        with pytest.raises(ValueError, match="NotFound"):
            await qdrant_service.delete_book(sample_book_id)
        
        # Verify count was called but delete was not
        qdrant_service.client.count.assert_called_once()
        qdrant_service.client.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_all_points_success(self, qdrant_service, sample_points):
        """Test successful retrieval of all points."""
        qdrant_service.client.scroll.return_value = (sample_points, None)
        
        result = await qdrant_service.get_all_points()
        
        assert result == sample_points
        qdrant_service.client.scroll.assert_called_once_with(
            collection_name="test_collection",
            with_payload=True,
            with_vectors=False,
            limit=999999
        )

    @pytest.mark.asyncio
    async def test_get_all_points_empty(self, qdrant_service):
        """Test retrieval when no points exist."""
        qdrant_service.client.scroll.return_value = ([], None)
        
        result = await qdrant_service.get_all_points()
        
        assert result == []
        qdrant_service.client.scroll.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_book_metadata_success(self, qdrant_service, sample_book_id):
        """Test successful book metadata update."""
        # Mock count result to show book exists
        mock_count_result = MagicMock()
        mock_count_result.count = 3
        qdrant_service.client.count.return_value = mock_count_result
        
        update_payload = {"name": "Updated Name", "author": "Updated Author"}
        
        await qdrant_service.update_book_metadata(sample_book_id, update_payload)
        
        # Verify count was called
        qdrant_service.client.count.assert_called_once()
        
        # Verify set_payload was called
        qdrant_service.client.set_payload.assert_called_once()
        set_payload_args = qdrant_service.client.set_payload.call_args
        assert set_payload_args[1]["collection_name"] == "test_collection"
        assert set_payload_args[1]["payload"] == update_payload
        assert set_payload_args[1]["wait"] is True

    @pytest.mark.asyncio
    async def test_update_book_metadata_not_found(self, qdrant_service, sample_book_id):
        """Test book metadata update when book doesn't exist."""
        # Mock count result to show book doesn't exist
        mock_count_result = MagicMock()
        mock_count_result.count = 0
        qdrant_service.client.count.return_value = mock_count_result
        
        update_payload = {"name": "Updated Name"}
        
        with pytest.raises(ValueError, match="NotFound"):
            await qdrant_service.update_book_metadata(sample_book_id, update_payload)
        
        # Verify count was called but set_payload was not
        qdrant_service.client.count.assert_called_once()
        qdrant_service.client.set_payload.assert_not_called()

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_success(self, qdrant_service, sample_book_id, sample_search_results):
        """Test successful semantic search in book."""
        qdrant_service.client.query_points.return_value = sample_search_results
        
        query_vector = [0.1, 0.2, 0.3]
        result = await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector,
            limit=5,
            score_threshold=0.7
        )
        
        # Verify result structure
        assert len(result) == 2
        assert result[0]["content"] == "Relevant content 1"
        assert result[0]["metadata"] == {"book_id": "book1", "name": "Test Book"}
        assert result[1]["content"] == "Relevant content 2"
        assert result[1]["metadata"] == {"book_id": "book1", "author": "Test Author"}
        
        # Verify query_points was called correctly
        qdrant_service.client.query_points.assert_called_once()
        call_args = qdrant_service.client.query_points.call_args
        assert call_args[1]["collection_name"] == "test_collection"
        assert call_args[1]["query"] == query_vector
        assert call_args[1]["limit"] == 5
        assert call_args[1]["score_threshold"] == 0.7
        assert call_args[1]["with_payload"] is True
        assert call_args[1]["with_vectors"] is False

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_no_results(self, qdrant_service, sample_book_id):
        """Test semantic search with no results."""
        mock_results = MagicMock()
        mock_results.points = []
        qdrant_service.client.query_points.return_value = mock_results
        
        query_vector = [0.1, 0.2, 0.3]
        result = await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector
        )
        
        assert result == []
        qdrant_service.client.query_points.assert_called_once()

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_default_parameters(self, qdrant_service, sample_book_id):
        """Test semantic search with default parameters."""
        mock_results = MagicMock()
        mock_results.points = []
        qdrant_service.client.query_points.return_value = mock_results
        
        query_vector = [0.1, 0.2, 0.3]
        await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector
        )
        
        # Verify default parameters were used
        call_args = qdrant_service.client.query_points.call_args
        assert call_args[1]["limit"] == 5
        assert call_args[1]["score_threshold"] == 0.7

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_custom_parameters(self, qdrant_service, sample_book_id):
        """Test semantic search with custom parameters."""
        mock_results = MagicMock()
        mock_results.points = []
        qdrant_service.client.query_points.return_value = mock_results
        
        query_vector = [0.1, 0.2, 0.3]
        await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector,
            limit=10,
            score_threshold=0.5
        )
        
        # Verify custom parameters were used
        call_args = qdrant_service.client.query_points.call_args
        assert call_args[1]["limit"] == 10
        assert call_args[1]["score_threshold"] == 0.5

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_point_without_payload(self, qdrant_service, sample_book_id):
        """Test semantic search when point has no payload."""
        mock_point1 = MagicMock()
        mock_point1.payload = {"content": "Content 1"}
        mock_point2 = MagicMock()
        mock_point2.payload = None  # No payload
        
        mock_results = MagicMock()
        mock_results.points = [mock_point1, mock_point2]
        qdrant_service.client.query_points.return_value = mock_results
        
        query_vector = [0.1, 0.2, 0.3]
        result = await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector
        )
        
        # Should only include point with payload
        assert len(result) == 1
        assert result[0]["content"] == "Content 1"
        assert result[0]["metadata"] == {}

    @pytest.mark.asyncio
    async def test_semantic_search_in_book_point_without_content(self, qdrant_service, sample_book_id):
        """Test semantic search when point payload has no content."""
        mock_point = MagicMock()
        mock_point.payload = {"book_id": "book1", "author": "Test Author"}  # No content field
        
        mock_results = MagicMock()
        mock_results.points = [mock_point]
        qdrant_service.client.query_points.return_value = mock_results
        
        query_vector = [0.1, 0.2, 0.3]
        result = await qdrant_service.semantic_search_in_book(
            book_id=sample_book_id,
            query_vector=query_vector
        )
        
        # Should include point with empty content
        assert len(result) == 1
        assert result[0]["content"] == ""
        assert result[0]["metadata"] == {"book_id": "book1", "author": "Test Author"}

    @pytest.mark.asyncio
    async def test_book_exists_true(self, qdrant_service, sample_book_id):
        """Test book_exists when book exists."""
        mock_count_result = MagicMock()
        mock_count_result.count = 5
        qdrant_service.client.count.return_value = mock_count_result
        
        result = await qdrant_service.book_exists(sample_book_id)
        
        assert result is True
        qdrant_service.client.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_book_exists_false(self, qdrant_service, sample_book_id):
        """Test book_exists when book doesn't exist."""
        mock_count_result = MagicMock()
        mock_count_result.count = 0
        qdrant_service.client.count.return_value = mock_count_result
        
        result = await qdrant_service.book_exists(sample_book_id)
        
        assert result is False
        qdrant_service.client.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_book_collection_filter_consistency(self, qdrant_service, sample_book_id):
        """Test that all methods use consistent collection name."""
        # Test multiple methods to ensure they all use the same collection
        mock_count_result = MagicMock()
        mock_count_result.count = 1
        qdrant_service.client.count.return_value = mock_count_result
        qdrant_service.client.scroll.return_value = ([], None)
        qdrant_service.client.query_points.return_value = MagicMock(points=[])
        
        # Test various methods
        await qdrant_service.book_exists(sample_book_id)
        await qdrant_service.get_all_points()
        await qdrant_service.semantic_search_in_book(sample_book_id, [0.1, 0.2, 0.3])
        
        # Verify all calls used the same collection name
        calls = qdrant_service.client.method_calls
        for call in calls:
            if "collection_name" in call[2]:
                assert call[2]["collection_name"] == "test_collection"
