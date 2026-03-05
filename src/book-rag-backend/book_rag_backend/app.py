import uvicorn
from fastapi import FastAPI
from typing import AsyncIterator
from book_rag_backend.api.routes import books_router, search_router
from fastapi.middleware.cors import CORSMiddleware
from fastembed import TextEmbedding
from qdrant_client import AsyncQdrantClient
from dotenv import load_dotenv
from loguru import logger
from book_rag_backend.config import load_config


load_dotenv()


def get_qdrant_client(url: str, api_key: str) -> AsyncQdrantClient:
    return AsyncQdrantClient(
        url=url,
        api_key=api_key,
        port=6333,
        https=True,
        timeout=60,
    )

async def lifespan(app: FastAPI) -> AsyncIterator:
    config = load_config(config_path="../config.yml")
    qdrant_client = get_qdrant_client(config.qdrant.url, config.qdrant.api_key)
    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    logger.info("Embeddings model loaded")

    app.state.qdrant_client = qdrant_client
    app.state.embedding_model = embedding_model
    app.state.config = config
    yield
    await qdrant_client.close()
    del embedding_model

app = FastAPI(
    title="Book RAG API",
    description="API for Book Retrieval-Augmented Generation system",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(books_router)
app.include_router(search_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

