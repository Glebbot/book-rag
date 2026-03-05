import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import UploadFile
import io

from book_rag_backend.services.books import BookService
from tests.mocks.mock_services import (
    MockQdrantService,
    MockParserService,
    MockSplitterService,
    MockEmbeddingsService
)


@pytest.fixture
def book_service():
    """Create a BookService instance with mock dependencies."""
    return BookService(
        qdrant=MockQdrantService(),
        parser=MockParserService(),
        splitter=MockSplitterService(),
        embeddings=MockEmbeddingsService()
    )


class TestBookService:
    """Test cases for BookService."""
    
    @pytest.mark.asyncio
    async def test_delete_book_success(self, book_service, sample_book_id):
        """Test successful book deletion."""
        # Add a book to delete
        book_service.qdrant.books[str(sample_book_id)] = {"id": sample_book_id}
        book_service.qdrant.points = [
            {
                "id": "point1",
                "vector": [0.1, 0.2, 0.3],
                "payload": {"book_id": str(sample_book_id), "content": "test"}
            }
        ]
        
        await book_service.delete_book(sample_book_id)
        
        assert str(sample_book_id) not in book_service.qdrant.books
        assert len(book_service.qdrant.points) == 1
    
    @pytest.mark.asyncio
    async def test_delete_book_not_found(self, book_service, sample_book_id):
        """Test book deletion when book not found."""
        with pytest.raises(ValueError, match="Book not found"):
            await book_service.delete_book(sample_book_id)
    
    @pytest.mark.asyncio
    async def test_list_books_success(self, book_service):
        """Test successful books listing."""
        book_id1 = uuid4()
        book_id2 = uuid4()
        
        # Mock points with different books - create proper mock objects
        mock_point1 = MagicMock()
        mock_point1.payload = {
            "book_id": str(book_id1),
            "name": "Test Book 1",
            "author": "Author 1",
            "year": 2021,
            "genres": ["Fiction"]
        }
        
        mock_point2 = MagicMock()
        mock_point2.payload = {
            "book_id": str(book_id2),
            "name": "Test Book 2",
            "author": "Author 2",
            "year": 2022,
            "genres": ["Non-Fiction"]
        }
        
        mock_point3 = MagicMock()
        mock_point3.payload = {
            "book_id": str(book_id1),  # Same book, different point
            "name": "Test Book 1",
            "author": "Author 1",
            "year": 2021,
            "genres": ["Fiction"]
        }
        
        book_service.qdrant.points = [mock_point1, mock_point2, mock_point3]
        
        books = await book_service.list_books()
        
        assert len(books) == 2
        book_ids = [book["id"] for book in books]
        assert book_id1 in book_ids
        assert book_id2 in book_ids
    
    @pytest.mark.asyncio
    async def test_list_books_empty(self, book_service):
        """Test books listing when no books exist."""
        book_service.qdrant.points = []
        
        books = await book_service.list_books()
        
        assert len(books) == 0
    
    @pytest.mark.asyncio
    async def test_update_book_success(self, book_service, sample_book_id):
        """Test successful book update."""
        # Add a book to update
        book_service.qdrant.books[str(sample_book_id)] = {"id": sample_book_id}
        book_service.qdrant.points = [
            {
                "id": "point1",
                "vector": [0.1, 0.2, 0.3],
                "payload": {
                    "book_id": str(sample_book_id),
                    "name": "Old Name",
                    "author": "Old Author"
                }
            }
        ]
        
        update_payload = {
            "name": "New Name",
            "author": "New Author"
        }
        
        await book_service.update_book(sample_book_id, update_payload)
        
        # Check that the point payload was updated
        point = book_service.qdrant.points[0]
        assert point["payload"]["author"] is not None
    
    @pytest.mark.asyncio
    async def test_update_book_not_found(self, book_service, sample_book_id):
        """Test book update when book not found."""
        update_payload = {"name": "New Name"}
        
        with pytest.raises(ValueError, match="Book not found"):
            await book_service.update_book(sample_book_id, update_payload)
    
    @pytest.mark.asyncio
    async def test_update_book_empty_payload(self, book_service, sample_book_id):
        """Test book update with empty payload."""
        with pytest.raises(ValueError, match="NotModified"):
            await book_service.update_book(sample_book_id, {})

    
    @pytest.mark.asyncio
    async def test_create_book_unsupported_format(self, book_service):
        """Test book creation with unsupported file format."""
        mock_file = MagicMock()
        mock_file.filename = "test.txt"
        
        with pytest.raises(TypeError, match="NotSupportedFormat"):
            await book_service.create_book(mock_file)
    
    @pytest.mark.asyncio
    async def test_create_book_empty_file(self, book_service):
        """Test book creation with empty file."""
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=b"")
        
        with pytest.raises(ValueError, match="BadFile"):
            await book_service.create_book(mock_file)
    
    @pytest.mark.asyncio
    async def test_create_book_no_filename(self, book_service):
        """Test book creation with no filename."""
        mock_file = MagicMock()
        mock_file.filename = None
        
        with pytest.raises(TypeError, match="NotSupportedFormat"):
            await book_service.create_book(mock_file)
    
    @pytest.mark.asyncio
    async def test_create_book_parsing_error(self, book_service, sample_pdf_content):
        """Test book creation when parsing fails."""
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=sample_pdf_content)
        
        # Mock parser to raise an exception
        book_service.parser.parse_pdf = MagicMock(side_effect=Exception("Parsing error"))
        
        with pytest.raises(ValueError, match="BadFile"):
            await book_service.create_book(mock_file)
    
    @pytest.mark.asyncio
    async def test_create_book_empty_parsed_text(self, book_service, sample_pdf_content):
        """Test book creation when parsed text is empty."""
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=sample_pdf_content)
        
        # Mock parser to return empty text
        book_service.parser.parse_pdf = MagicMock(return_value="")
        
        with pytest.raises(ValueError, match="BadFile"):
            await book_service.create_book(mock_file)
    
    @pytest.mark.asyncio
    async def test_create_book_splitting_error(self, book_service, sample_pdf_content):
        """Test book creation when splitting fails."""
        mock_file = MagicMock()
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=sample_pdf_content)
        
        # Mock splitter to return empty chunks
        book_service.splitter.split = MagicMock(return_value=[])
        
        with pytest.raises(ValueError, match="BadFile"):
            await book_service.create_book(mock_file)
