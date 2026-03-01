import os
from functools import lru_cache
from qdrant_client import AsyncQdrantClient
from ..services.qdrant import QdrantService
from ..services.books import BookService
from ..services.parser import ParserService  # заглушки, замени на свои
from ..services.splitter import SplitterService
from ..services.embeddings import EmbeddingsService
from dotenv import load_dotenv

load_dotenv()

@lru_cache
def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY"),
        port=6333,
        https=True,
        timeout=60,
    )


@lru_cache
def get_qdrant_service() -> QdrantService:
    return QdrantService(
        client=get_qdrant_client(),
        collection=os.getenv("QDRANT_COLLECTION")
    )


def get_parser_service() -> ParserService:
    return ParserService()  # передай конфиги если нужны


def get_splitter_service() -> SplitterService:
    return SplitterService(chunk_size=500, chunk_overlap=50)


def get_embeddings_service() -> EmbeddingsService:
    return EmbeddingsService(model="text-embedding-3-small")  # или другая модель


@lru_cache
def get_book_service() -> BookService:
    return BookService(
        qdrant=get_qdrant_service(),
        parser=get_parser_service(),
        splitter=get_splitter_service(),
        embeddings=get_embeddings_service(),
    )