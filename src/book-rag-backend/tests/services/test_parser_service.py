import pytest
from unittest.mock import MagicMock, patch

from book_rag_backend.services.parser import ParserService


class TestParserService:
    """Test cases for ParserService."""
    
    @pytest.fixture
    def parser_service(self):
        """Create a ParserService instance."""
        return ParserService()
    
    def test_parse_pdf_success(self, parser_service):
        """Test successful PDF parsing."""
        # Mock pdfplumber to avoid actual PDF parsing
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is test PDF content"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page, mock_page]  # Two pages
        
        with patch('pdfplumber.open') as mock_open:
            mock_open.return_value.__enter__.return_value = mock_pdf
            result = parser_service.parse_pdf(b"mock PDF content")
        
        assert isinstance(result, str)
        assert "This is test PDF content" in result
        assert result.count("This is test PDF content") == 2  # Two pages
    
    def test_parse_pdf_single_page(self, parser_service):
        """Test PDF parsing with single page."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Single page content"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open') as mock_open:
            mock_open.return_value.__enter__.return_value = mock_pdf
            result = parser_service.parse_pdf(b"single page PDF")
        
        assert result == "Single page content"

    
    def test_parse_pdf_exception_handling(self, parser_service):
        """Test PDF parsing when an exception occurs."""
        with patch('pdfplumber.open', side_effect=Exception("PDF parsing error")):
            with pytest.raises(Exception, match="PDF parsing error"):
                parser_service.parse_pdf(b"invalid PDF")
    
    def test_parse_pdf_page_extraction_error(self, parser_service):
        """Test PDF parsing when page text extraction fails."""
        mock_page = MagicMock()
        mock_page.extract_text.side_effect = Exception("Page extraction error")
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open') as mock_open:
            mock_open.return_value.__enter__.return_value = mock_pdf
            with pytest.raises(Exception, match="Page extraction error"):
                parser_service.parse_pdf(b"PDF with extraction error")
    
    def test_parse_pdf_unicode_content(self, parser_service):
        """Test PDF parsing with Unicode content."""
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Тестовый контент на русском языке"
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open') as mock_open:
            mock_open.return_value.__enter__.return_value = mock_pdf
            result = parser_service.parse_pdf(b"unicode PDF")
        
        assert "Тестовый контент на русском языке" in result
    
    def test_parse_pdf_large_content(self, parser_service):
        """Test PDF parsing with large content."""
        large_content = "A" * 10000  # Large content
        mock_page = MagicMock()
        mock_page.extract_text.return_value = large_content
        
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        
        with patch('pdfplumber.open') as mock_open:
            mock_open.return_value.__enter__.return_value = mock_pdf
            result = parser_service.parse_pdf(b"large PDF")
        
        assert len(result) == 10000
        assert result == large_content
