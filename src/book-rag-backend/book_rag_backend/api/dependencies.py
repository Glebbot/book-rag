import os
from fastapi import Depends, Request
from book_rag_backend.services.qdrant import QdrantService
from book_rag_backend.services.books import BookService
from book_rag_backend.services.parser import ParserService
from book_rag_backend.services.splitter import SplitterService
from book_rag_backend.services.embeddings import EmbeddingsService
from ..services.llm import LLMService
from ..services.rag import RAGService
from dotenv import load_dotenv

load_dotenv()

def get_qdrant_service(request: Request) -> QdrantService:
    return QdrantService(
        client=request.app.state.qdrant_client,
        collection=request.app.state.config.qdrant.collection_name
    )


def get_parser_service() -> ParserService:
    return ParserService()


def get_splitter_service(request: Request) -> SplitterService:
    splitters_config = request.app.state.config.splitter
    return SplitterService(chunk_size=splitters_config.chunk_size, chunk_overlap=splitters_config.chunk_overlap)


def get_embeddings_service(request: Request) -> EmbeddingsService:
    return EmbeddingsService(model=request.app.state.embedding_model)


def get_book_service(qdrant_service: QdrantService = Depends(get_qdrant_service),
                     parser_service: ParserService = Depends(get_parser_service),
                     splitter_service: SplitterService = Depends(get_splitter_service),
                     embeddings_service: EmbeddingsService = Depends(get_embeddings_service)) -> BookService:
    return BookService(
        qdrant=qdrant_service,
        parser=parser_service,
        splitter=splitter_service,
        embeddings=embeddings_service,
    )

def get_llm_service(request: Request) -> LLMService:
    llm_cfg = request.app.state.config.model
    return LLMService(
        base_url=llm_cfg.url,
        api_key=os.getenv("OPENAI_API_KEY") or llm_cfg.api_key,
        model=llm_cfg.model,
        timeout=600,
        max_tokens=200000,
    )


def get_rag_service(
        _request: Request,
        qdrant_service: QdrantService = Depends(get_qdrant_service),
        embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
        llm_service: LLMService = Depends(get_llm_service),
) -> RAGService:
    return RAGService(
        qdrant=qdrant_service,
        embeddings=embeddings_service,
        llm=llm_service,
        top_k=10,
        score_threshold=0.5,
        max_context_tokens=200000,
    )