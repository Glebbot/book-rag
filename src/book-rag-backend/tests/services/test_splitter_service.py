import pytest
from unittest.mock import MagicMock, patch

from book_rag_backend.services.splitter import SplitterService


class TestSplitterService:
    """Test cases for SplitterService."""
    
    @pytest.fixture
    def splitter_service(self):
        """Create a SplitterService instance with default parameters."""
        return SplitterService(chunk_size=1000, chunk_overlap=200)
    
    def test_splitter_initialization(self):
        """Test SplitterService initialization."""
        splitter = SplitterService(chunk_size=500, chunk_overlap=100)
        assert hasattr(splitter, 'splitter')
        assert splitter.splitter._chunk_size == 500
        assert splitter.splitter._chunk_overlap == 100
    
    def test_split_short_text(self, splitter_service):
        """Test splitting text shorter than chunk size."""
        short_text = "This is a short text."
        
        result = splitter_service.split(short_text)
        
        assert result == [short_text]
    
    def test_split_long_text(self, splitter_service):
        """Test splitting text longer than chunk size."""
        long_text = "This is a very long text. " * 100
        
        result = splitter_service.split(long_text)
        
        assert isinstance(result, list)
        assert len(result) > 1
        assert all(isinstance(chunk, str) for chunk in result)
    
    def test_split_empty_text(self, splitter_service):
        """Test splitting empty text."""
        result = splitter_service.split("")
        
        assert result == []
    
    def test_split_with_different_parameters(self):
        """Test splitting with different chunk parameters."""
        splitter = SplitterService(chunk_size=200, chunk_overlap=50)
        text = "Sample text for testing. " * 50
        
        result = splitter.split(text)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_split_unicode_text(self, splitter_service):
        """Test splitting Unicode text."""
        unicode_text = "Тестовый текст на русском языке. " * 50
        
        result = splitter_service.split(unicode_text)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("Тестовый текст" in chunk for chunk in result)
    
    def test_split_with_special_characters(self, splitter_service):
        """Test splitting text with special characters."""
        special_text = "Text\n\nwith\n\nvarious\n\nseparators. " * 20
        
        result = splitter_service.split(special_text)
        
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_split_single_chunk(self, splitter_service):
        """Test splitting text that results in single chunk."""
        text = "Short text"
        
        result = splitter_service.split(text)
        
        assert result == [text]
    
    def test_splitter_error_handling(self, splitter_service):
        """Test error handling in splitter."""
        text = "Test text"
        
        # The splitter should handle errors gracefully
        result = splitter_service.split(text)
        
        assert isinstance(result, list)
