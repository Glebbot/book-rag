import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError

from book_rag_backend.api.schemas.books import (
    ErrorResponse,
    BookShort,
    BooksListResponse,
    BookUpdateRequest
)


class TestBooksSchemas:
    """Test cases for books schemas."""
    
    def test_error_response_schema(self):
        """Test ErrorResponse schema."""
        error = ErrorResponse(errorCode="NotFound", userMessage="Book not found")
        
        assert error.errorCode == "NotFound"
        assert error.userMessage == "Book not found"
    
    def test_book_short_schema(self):
        """Test BookShort schema."""
        book_id = uuid4()
        book = BookShort(
            id=book_id,
            name="Test Book",
            year=2021,
            genres=["Fiction", "Mystery"],
            author="Test Author"
        )
        
        assert book.id == book_id
        assert book.name == "Test Book"
        assert book.year == 2021
        assert book.genres == ["Fiction", "Mystery"]
        assert book.author == "Test Author"
    
    def test_book_short_schema_minimal(self):
        """Test BookShort schema with minimal required fields."""
        book_id = uuid4()
        book = BookShort(id=book_id, name="Test Book")
        
        assert book.id == book_id
        assert book.name == "Test Book"
        assert book.year is None
        assert book.genres is None
        assert book.author is None
    
    def test_books_list_response_schema(self):
        """Test BooksListResponse schema."""
        book_id1 = uuid4()
        book_id2 = uuid4()
        
        books = [
            BookShort(id=book_id1, name="Book 1"),
            BookShort(id=book_id2, name="Book 2", author="Author 2")
        ]
        
        response = BooksListResponse(books=books)
        
        assert len(response.books) == 2
        assert response.books[0].name == "Book 1"
        assert response.books[1].name == "Book 2"
        assert response.books[1].author == "Author 2"
    
    def test_book_update_request_schema_all_fields(self):
        """Test BookUpdateRequest schema with all fields."""
        update_request = BookUpdateRequest(
            name="Updated Book Name",
            year=2023,
            genres=["Fiction", "Science Fiction"],
            author="Updated Author"
        )
        
        assert update_request.name == "Updated Book Name"
        assert update_request.year == 2023
        assert update_request.genres == ["Fiction", "Science Fiction"]
        assert update_request.author == "Updated Author"
    
    def test_book_update_request_schema_partial_fields(self):
        """Test BookUpdateRequest schema with partial fields."""
        update_request = BookUpdateRequest(
            name="New Name",
            author="New Author"
        )
        
        assert update_request.name == "New Name"
        assert update_request.author == "New Author"
        assert update_request.year is None
        assert update_request.genres is None
    
    def test_book_update_request_schema_empty(self):
        """Test BookUpdateRequest schema with no fields."""
        update_request = BookUpdateRequest()
        
        assert update_request.name is None
        assert update_request.year is None
        assert update_request.genres is None
        assert update_request.author is None
    
    def test_book_update_request_name_validation_empty_string(self):
        """Test BookUpdateRequest name validation with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(name="   ")
        
        assert "Name can't be empty" in str(exc_info.value)
    
    def test_book_update_request_name_valid_whitespace(self):
        """Test BookUpdateRequest name validation with valid whitespace handling."""
        update_request = BookUpdateRequest(name="  Valid Name  ")
        assert update_request.name == "  Valid Name  "
    
    def test_book_update_request_author_validation_empty_string(self):
        """Test BookUpdateRequest author validation with empty string."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(author="\t\n")
        
        assert "Author can't be empty" in str(exc_info.value)
    
    def test_book_update_request_author_valid_whitespace(self):
        """Test BookUpdateRequest author validation with valid whitespace handling."""
        update_request = BookUpdateRequest(author="  Valid Author  ")
        assert update_request.author == "  Valid Author  "
    
    def test_book_update_request_year_validation_negative(self):
        """Test BookUpdateRequest year validation with negative year."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(year=-1)
        
        assert "Invalid year" in str(exc_info.value)
    
    def test_book_update_request_year_validation_future(self):
        """Test BookUpdateRequest year validation with future year."""
        future_year = datetime.now().year + 1
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(year=future_year)
        
        assert "Invalid year" in str(exc_info.value)
    
    def test_book_update_request_year_valid_boundaries(self):
        """Test BookUpdateRequest year validation with valid boundary years."""
        current_year = datetime.now().year
        
        # Test year 0
        update_request = BookUpdateRequest(year=0)
        assert update_request.year == 0
        
        # Test current year
        update_request = BookUpdateRequest(year=current_year)
        assert update_request.year == current_year
    
    def test_book_update_request_genres_validation_not_list(self):
        """Test BookUpdateRequest genres validation when not a list."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(genres="Fiction")
        
        assert "list_type" in str(exc_info.value)
    
    def test_book_update_request_genres_validation_empty_string(self):
        """Test BookUpdateRequest genres validation with empty string in list."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(genres=["Fiction", "", "Mystery"])
        
        assert "Genre can't be empty" in str(exc_info.value)
    
    def test_book_update_request_genres_validation_not_string(self):
        """Test BookUpdateRequest genres validation with non-string items."""
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(genres=["Fiction", 123, "Mystery"])
        
        assert "string_type" in str(exc_info.value)
    
    def test_book_update_request_genres_validation_too_long(self):
        """Test BookUpdateRequest genres validation with genre too long."""
        long_genre = "A" * 101  # 101 characters
        with pytest.raises(ValidationError) as exc_info:
            BookUpdateRequest(genres=["Fiction", long_genre])
        
        assert "Genre can't be longer than 100 characters" in str(exc_info.value)

    
    def test_book_update_request_genres_max_length_boundary(self):
        """Test BookUpdateRequest genres validation at max length boundary."""
        max_genre = "A" * 100  # Exactly 100 characters
        update_request = BookUpdateRequest(genres=[max_genre])
        assert update_request.genres == [max_genre]
    
    def test_book_update_request_name_max_length(self):
        """Test BookUpdateRequest name max length validation."""
        max_name = "A" * 100  # Exactly 100 characters
        update_request = BookUpdateRequest(name=max_name)
        assert update_request.name == max_name
    
    def test_book_update_request_name_too_long(self):
        """Test BookUpdateRequest name validation when too long."""
        long_name = "A" * 101  # 101 characters
        with pytest.raises(ValidationError):
            BookUpdateRequest(name=long_name)
    
    def test_book_update_request_author_max_length(self):
        """Test BookUpdateRequest author max length validation."""
        max_author = "A" * 100  # Exactly 100 characters
        update_request = BookUpdateRequest(author=max_author)
        assert update_request.author == max_author
    
    def test_book_update_request_author_too_long(self):
        """Test BookUpdateRequest author validation when too long."""
        long_author = "A" * 101  # 101 characters
        with pytest.raises(ValidationError):
            BookUpdateRequest(author=long_author)
