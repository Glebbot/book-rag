from book_rag_backend.api.routes.books import router as books_router
from book_rag_backend.api.routes.search import router as search_router

__all__ = [
    "books_router",
    "search_router",
]
