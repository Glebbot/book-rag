import pytest
from pydantic import ValidationError

from book_rag_backend.api.schemas.search import SearchRequest, SearchResponse, Message, MessageRole


class TestSearchSchemas:
    """Test cases for search schemas."""
    
    def test_message_schema(self):
        """Test Message schema."""
        message = Message(role=MessageRole.user, content="What is this book about?")
        
        assert message.role == MessageRole.user
        assert message.content == "What is this book about?"
    
    def test_message_schema_assistant(self):
        """Test Message schema with assistant role."""
        message = Message(role=MessageRole.assistant, content="This is a book about...")
        
        assert message.role == MessageRole.assistant
        assert message.content == "This is a book about..."
    
    def test_search_request_schema_single_message(self):
        """Test SearchRequest schema with single message."""
        request = SearchRequest(messages=[
            Message(role=MessageRole.user, content="Test question")
        ])
        
        assert len(request.messages) == 1
        assert request.messages[0].role == MessageRole.user
        assert request.messages[0].content == "Test question"
    
    def test_search_request_schema_multiple_messages(self):
        """Test SearchRequest schema with multiple messages."""
        request = SearchRequest(messages=[
            Message(role=MessageRole.user, content="First question"),
            Message(role=MessageRole.assistant, content="First answer"),
            Message(role=MessageRole.user, content="Second question")
        ])
        
        assert len(request.messages) == 3
        assert request.messages[0].role == MessageRole.user
        assert request.messages[1].role == MessageRole.assistant
        assert request.messages[2].role == MessageRole.user
    
    def test_search_request_schema_empty_messages(self):
        """Test SearchRequest schema with empty messages list."""
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(messages=[])
        assert "too_short" in str(exc_info.value)
    
    def test_search_response_schema_single_message(self):
        """Test SearchResponse schema with single message."""
        response = SearchResponse(messages=[
            Message(role=MessageRole.assistant, content="This is the answer")
        ])
        
        assert len(response.messages) == 1
        assert response.messages[0].role == MessageRole.assistant
        assert response.messages[0].content == "This is the answer"
    
    def test_search_response_schema_conversation(self):
        """Test SearchResponse schema with conversation history."""
        response = SearchResponse(messages=[
            Message(role=MessageRole.user, content="Original question"),
            Message(role=MessageRole.assistant, content="Original answer"),
            Message(role=MessageRole.user, content="Follow-up question"),
            Message(role=MessageRole.assistant, content="Follow-up answer")
        ])
        
        assert len(response.messages) == 4
        assert response.messages[0].role == MessageRole.user
        assert response.messages[1].role == MessageRole.assistant
        assert response.messages[2].role == MessageRole.user
        assert response.messages[3].role == MessageRole.assistant
    
    def test_search_response_schema_empty(self):
        """Test SearchResponse schema with empty messages."""
        response = SearchResponse(messages=[])
        
        assert len(response.messages) == 0
    
    def test_message_schema_long_content(self):
        """Test Message schema with long content."""
        long_content = "A" * 10000  # Very long content
        message = Message(role=MessageRole.user, content=long_content)
        
        assert message.content == long_content
        assert len(message.content) == 10000
    
    def test_message_schema_unicode_content(self):
        """Test Message schema with Unicode content."""
        unicode_content = "Тестовый вопрос на русском языке"
        message = Message(role=MessageRole.user, content=unicode_content)
        
        assert message.content == unicode_content
        assert "Тестовый вопрос" in message.content
    
    def test_message_schema_special_characters(self):
        """Test Message schema with special characters."""
        special_content = "Question with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        message = Message(role=MessageRole.user, content=special_content)
        
        assert message.content == special_content
    
    def test_message_schema_newlines(self):
        """Test Message schema with newlines."""
        multiline_content = "Line 1\nLine 2\nLine 3"
        message = Message(role=MessageRole.user, content=multiline_content)
        
        assert message.content == multiline_content
        assert message.content.count("\n") == 2
    
    def test_search_request_model_dump(self):
        """Test SearchRequest model_dump method."""
        request = SearchRequest(messages=[
            Message(role=MessageRole.user, content="Test message")
        ])
        
        dumped = request.model_dump()
        
        assert "messages" in dumped
        assert len(dumped["messages"]) == 1
        assert dumped["messages"][0]["role"] == "user"
        assert dumped["messages"][0]["content"] == "Test message"
    
    def test_message_model_dump(self):
        """Test Message model_dump method."""
        message = Message(role=MessageRole.user, content="Test message")
        
        dumped = message.model_dump()
        
        assert dumped["role"] == "user"
        assert dumped["content"] == "Test message"
    
    def test_search_response_from_dict(self):
        """Test creating SearchResponse from dict data."""
        data = {
            "messages": [
                {"role": "user", "content": "Question"},
                {"role": "assistant", "content": "Answer"}
            ]
        }
        
        response = SearchResponse(**data)
        
        assert len(response.messages) == 2
        assert response.messages[0].role == MessageRole.user
        assert response.messages[1].role == MessageRole.assistant
    
    def test_message_invalid_role(self):
        """Test Message schema with invalid role."""
        # This should raise a validation error due to enum
        with pytest.raises(ValidationError):
            Message(role="invalid_role", content="Test content")
    
    def test_search_request_with_none_messages(self):
        """Test SearchRequest with None messages."""
        # This should raise a validation error
        with pytest.raises(ValidationError):
            SearchRequest(messages=None)
    
    def test_message_empty_content(self):
        """Test Message with empty content."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role=MessageRole.user, content="")
        assert "string_too_short" in str(exc_info.value)
    
    def test_message_whitespace_content(self):
        """Test Message with whitespace-only content."""
        with pytest.raises(ValidationError) as exc_info:
            Message(role=MessageRole.user, content="   \t\n   ")
        assert "Content can't be empty" in str(exc_info.value)
