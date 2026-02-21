from fastapi import FastAPI
from book_rag_backend.api.routes import books_router, search_router

app = FastAPI(
    title="Book RAG API",
    description="API for Book Retrieval-Augmented Generation system",
    version="1.0.0"
)

app.include_router(books_router)
app.include_router(search_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


