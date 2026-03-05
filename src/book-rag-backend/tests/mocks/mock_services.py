from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from typing import List, Dict, Any


class MockQdrantService:
    """Mock implementation of QdrantService for testing."""
    
    def __init__(self):
        self.client = AsyncMock()
        self.collection = "test_collection"
        self.books = {}
        self.points = []
    
    async def delete_book(self, book_id: UUID):
        """Mock delete book method."""
        if str(book_id) in self.books:
            del self.books[str(book_id)]
            self.points = [p for p in self.points if p.get("book_id") != str(book_id)]
        else:
            raise ValueError("Book not found")
    
    async def get_all_points(self):
        """Mock get all points method."""
        mock_points = []
        for point in self.points:
            mock_point = MagicMock()
            mock_point.payload = point.payload
            mock_points.append(mock_point)
        return mock_points
    
    async def update_book_metadata(self, book_id: UUID, update_payload: dict):
        """Mock update book metadata method."""
        if str(book_id) not in self.books:
            raise ValueError("Book not found")

    
    async def book_exists(self, book_id: UUID) -> bool:
        """Mock book exists method."""
        return str(book_id) in self.books
    
    async def semantic_search_in_book(
        self, 
        book_id: UUID, 
        query_vector: List[float], 
        limit: int = 5, 
        score_threshold: float = 0.7
    ):
        """Mock semantic search method."""
        if str(book_id) not in self.books:
            raise ValueError("Book not found")
        
        # Return mock chunks
        return [
            {"content": f"Mock content chunk {i} for book {book_id}", "score": 0.8}
            for i in range(min(limit, 3))
        ]


class MockParserService:
    """Mock implementation of ParserService for testing."""
    
    def parse_pdf(self, content: bytes) -> str:
        """Mock PDF parsing method."""
        if not content:
            raise ValueError("Empty content")
        return "This is mock parsed PDF content for testing purposes. " * 50


class MockSplitterService:
    """Mock implementation of SplitterService for testing."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str) -> List[str]:
        """Mock text splitting method."""
        if not text:
            return []
        
        # Simple mock splitting - return chunks based on text length
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                overlap_words = current_chunk[-min(self.chunk_overlap // 10, len(current_chunk)):] if self.chunk_overlap > 0 else []
                current_chunk = overlap_words
                current_length = sum(len(w) for w in current_chunk)
            
            current_chunk.append(word)
            current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks if chunks else [text]


class MockEmbeddingsService:
    """Mock implementation of EmbeddingsService for testing."""
    
    def __init__(self, model=None):
        self.model = model or MagicMock()
    
    def embed(self, text: str) -> List[float]:
        """Mock single text embedding method."""
        # Return a deterministic vector based on text hash
        hash_val = hash(text) % 1000
        return [float((hash_val + i) % 100) / 100 for i in range(380)]
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Mock batch embedding method."""
        return [self.embed(text) for text in texts]


class MockLLMService:
    """Mock implementation of LLMService for testing."""
    
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int = 600, max_tokens: int = 200000):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_tokens = max_tokens
    
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        """Mock LLM generation method."""
        # Return a mock response based on the last user message
        user_messages = [msg for msg in messages if msg["role"] == "user"]
        if user_messages:
            last_message = user_messages[-1]["content"]
            if "контекст" in last_message.lower():
                return "Based on the provided context from the book, here is my response..."
            return f"This is a mock LLM response to: {last_message[:50]}..."
        return "This is a mock LLM response."


class MockBookService:
    """Mock implementation of BookService for testing."""
    
    def __init__(self):
        self.qdrant = MockQdrantService()
        self.parser = MockParserService()
        self.splitter = MockSplitterService()
        self.embeddings = MockEmbeddingsService()
    
    async def delete_book(self, book_id: UUID):
        """Mock delete book method."""
        await self.qdrant.delete_book(book_id)
    
    async def list_books(self):
        """Mock list books method."""
        return await self.qdrant.get_all_points()
    
    async def update_book(self, book_id: UUID, update_payload: dict):
        """Mock update book method."""
        await self.qdrant.update_book_metadata(book_id, update_payload)
    
    async def create_book(self, file) -> UUID:
        """Mock create book method."""
        from uuid import uuid4
        
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise TypeError("NotSupportedFormat")
        
        content = await file.read()
        if not content:
            raise ValueError("BadFile")
        
        text = self.parser.parse_pdf(content)
        chunks = self.splitter.split(text)
        vectors = self.embeddings.embed_batch(chunks)
        
        book_id = uuid4()
        name = file.filename.rsplit(".", 1)[0]
        
        # Create mock points
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            point = {
                "id": str(uuid4()),
                "vector": vector,
                "payload": {
                    "content": chunk,
                    "book_id": str(book_id),
                    "name": name,
                    "author": None,
                    "year": None,
                    "genres": None,
                },
            }
            self.qdrant.points.append(point)
        
        self.qdrant.books[str(book_id)] = {
            "id": book_id,
            "name": name,
            "author": None,
            "year": None,
            "genres": None,
        }
        
        return book_id


class MockRAGService:
    """Mock implementation of RAGService for testing."""
    
    def __init__(self):
        self.qdrant = MockQdrantService()
        self.embeddings = MockEmbeddingsService()
        self.llm = MockLLMService("http://localhost:11434", "test_key", "llama2")
        self.top_k = 10
        self.score_threshold = 0.5
        self.max_context_tokens = 200000
    
    async def search_in_book(self, book_id: UUID, messages: List[dict]) -> List[dict]:
        """Mock search in book method."""
        if not await self.qdrant.book_exists(book_id):
            raise ValueError("NotFound")
        
        # Mock the search process
        user_question = messages[-1]["content"]
        query_vector = self.embeddings.embed(user_question)
        
        chunks = await self.qdrant.semantic_search_in_book(
            book_id=book_id,
            query_vector=query_vector,
            limit=self.top_k,
            score_threshold=self.score_threshold,
        )
        
        # Generate mock response
        mock_response = f"Based on the book content, here's an answer to: {user_question}"
        
        return messages + [{"role": "assistant", "content": mock_response}]
