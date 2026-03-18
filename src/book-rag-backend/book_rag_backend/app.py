import uvicorn
from fastapi import FastAPI
from typing import AsyncIterator
from book_rag_backend.api.routes import books_router, search_router
from fastapi.middleware.cors import CORSMiddleware
from fastembed import TextEmbedding
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
from loguru import logger
from book_rag_backend.config import load_config
from pathlib import Path

APP_DIR = Path(__file__).parent
PROJECT_ROOT = APP_DIR.parent

load_dotenv()


def get_qdrant_client(url: str, api_key: str | None) -> AsyncQdrantClient:
    """Создаёт клиент Qdrant с правильной настройкой для http/https"""
    # Для локального http не передаём api_key и не включаем https
    kwargs = {
        "url": url,
        "port": 6333,
        "timeout": 60
    }

    # Ключ и https только для защищённых соединений
    if api_key and url.startswith("https"):
        kwargs["api_key"] = api_key
        kwargs["https"] = True

    return AsyncQdrantClient(**kwargs)


async def lifespan(app: FastAPI) -> AsyncIterator:
    config = load_config(config_path=PROJECT_ROOT / "config.yml")

    qdrant_client = get_qdrant_client(config.qdrant.url, config.qdrant.api_key)

    collection_name = config.qdrant.collection_name
    try:
        if not await qdrant_client.collection_exists(collection_name):
            logger.info(f"Creating collection: {collection_name}")
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            # 🔹 Индекс для фильтрации по book_id (как в QdrantService)
            await qdrant_client.create_payload_index(
                collection_name=collection_name,
                field_name="book_id",
                field_schema="keyword",
            )
            logger.success(f"✓ Collection '{collection_name}' created with indexes")
        else:
            logger.info(f"✓ Collection '{collection_name}' already exists")
    except Exception as e:
        logger.error(f"Failed to ensure collection: {e}")
        raise

    embedding_model = TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    logger.info("✓ Embeddings model loaded")

    app.state.qdrant_client = qdrant_client
    app.state.embedding_model = embedding_model
    app.state.config = config

    yield

    await qdrant_client.close()
    del embedding_model
    logger.info("Resources cleaned up")


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