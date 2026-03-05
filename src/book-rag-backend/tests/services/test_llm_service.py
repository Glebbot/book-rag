import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from book_rag_backend.services.llm import LLMService


@pytest.fixture
def llm_service():
    """Create a LLMService instance for testing."""
    return LLMService(
        base_url="https://api.example.com",
        api_key="test_api_key",
        model="test-model",
        timeout=30,
        max_tokens=1000
    )


@pytest.fixture
def sample_messages():
    """Create sample chat messages for testing."""
    return [
        {"role": "user", "content": "What is this book about?"},
        {"role": "assistant", "content": "This is a sample book for testing."},
        {"role": "user", "content": "Tell me more about the main topic."},
    ]


@pytest.fixture
def sample_llm_response():
    """Create sample LLM API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the LLM."
                }
            }
        ]
    }


class TestLLMService:
    """Test cases for LLMService."""

    def test_init_default_values(self):
        """Test LLMService initialization with default values."""
        service = LLMService(
            base_url="https://api.example.com/",
            api_key="test_key"
        )
        
        assert service.base_url == "https://api.example.com"
        assert service.api_key == "test_key"
        assert service.model == "deepseek-chat"
        assert service.timeout == 600
        assert service.max_tokens == 200000
        assert service._client is None

    def test_init_custom_values(self):
        """Test LLMService initialization with custom values."""
        service = LLMService(
            base_url="https://custom-api.com/v1/",
            api_key="custom_key",
            model="custom-model",
            timeout=120,
            max_tokens=4000
        )
        
        assert service.base_url == "https://custom-api.com/v1"
        assert service.api_key == "custom_key"
        assert service.model == "custom-model"
        assert service.timeout == 120
        assert service.max_tokens == 4000
        assert service._client is None

    @pytest.mark.asyncio
    async def test_get_client_creates_new_client(self, llm_service):
        """Test that _get_client creates a new httpx.AsyncClient."""
        client = await llm_service._get_client()
        
        assert client is not None
        assert isinstance(client, httpx.AsyncClient)
        assert client.headers["Authorization"] == f"Bearer {llm_service.api_key}"
        assert client.headers["Content-Type"] == "application/json"
        
        # Clean up
        await client.aclose()

    @pytest.mark.asyncio
    async def test_get_client_reuses_existing_client(self, llm_service):
        """Test that _get_client reuses existing client."""
        client1 = await llm_service._get_client()
        client2 = await llm_service._get_client()
        
        assert client1 is client2
        
        # Clean up
        await client1.aclose()

    @pytest.mark.asyncio
    async def test_close_closes_client(self, llm_service):
        """Test that close properly closes the client."""
        client = await llm_service._get_client()
        assert llm_service._client is not None
        
        await llm_service.close()
        
        assert llm_service._client is None

    @pytest.mark.asyncio
    async def test_close_no_client(self, llm_service):
        """Test that close handles case when no client exists."""
        # Should not raise an exception
        await llm_service.close()
        assert llm_service._client is None

    @pytest.mark.asyncio
    async def test_generate_success(self, llm_service, sample_messages, sample_llm_response):
        """Test successful message generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_llm_response
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            result = await llm_service.generate(sample_messages)
            
            assert result == "This is a test response from the LLM."
            mock_client.post.assert_called_once_with(
                f"{llm_service.base_url}/v1/chat/completions",
                json={
                    "model": llm_service.model,
                    "messages": sample_messages,
                    "temperature": 0.0,
                }
            )

    @pytest.mark.asyncio
    async def test_generate_with_custom_temperature(self, llm_service, sample_messages, sample_llm_response):
        """Test message generation with custom temperature."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_llm_response
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            await llm_service.generate(sample_messages, temperature=0.7)
            
            mock_client.post.assert_called_once_with(
                f"{llm_service.base_url}/v1/chat/completions",
                json={
                    "model": llm_service.model,
                    "messages": sample_messages,
                    "temperature": 0.7,
                }
            )

    @pytest.mark.asyncio
    async def test_generate_http_error(self, llm_service, sample_messages):
        """Test generate method when HTTP error occurs."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "API Error", request=MagicMock(), response=mock_response
        )
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(httpx.HTTPStatusError):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_generate_invalid_json_response(self, llm_service, sample_messages):
        """Test generate method when response contains invalid JSON."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(ValueError, match="Invalid JSON"):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_generate_missing_response_fields(self, llm_service, sample_messages):
        """Test generate method when response is missing expected fields."""
        # Test missing choices
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(KeyError):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_generate_empty_choices(self, llm_service, sample_messages):
        """Test generate method when response has empty choices."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            with pytest.raises(IndexError):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_generate_network_error(self, llm_service, sample_messages):
        """Test generate method when network error occurs."""
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.RequestError("Network error")
            mock_get_client.return_value = mock_client
            
            with pytest.raises(httpx.RequestError):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_generate_timeout_error(self, llm_service, sample_messages):
        """Test generate method when timeout occurs."""
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
            mock_get_client.return_value = mock_client
            
            with pytest.raises(httpx.TimeoutException):
                await llm_service.generate(sample_messages)

    @pytest.mark.asyncio
    async def test_multiple_generate_calls_reuse_client(self, llm_service, sample_messages, sample_llm_response):
        """Test that multiple generate calls reuse the same client."""
        mock_response = MagicMock()
        mock_response.json.return_value = sample_llm_response
        mock_response.raise_for_status.return_value = None
        
        with patch.object(llm_service, '_get_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_get_client.return_value = mock_client
            
            await llm_service.generate(sample_messages)
            await llm_service.generate(sample_messages)
            
            # _get_client should be called twice, but client.post should be called twice
            assert mock_get_client.call_count == 2
            assert mock_client.post.call_count == 2
