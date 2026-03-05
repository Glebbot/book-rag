from fastapi import Depends, Request
from book_rag_backend.services.qdrant import QdrantService
from book_rag_backend.services.books import BookService
from book_rag_backend.services.parser import ParserService
from book_rag_backend.services.splitter import SplitterService
from book_rag_backend.services.embeddings import EmbeddingsService


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
