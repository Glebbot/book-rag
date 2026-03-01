import random


class EmbeddingsService:
    """Заглушка: генерирует случайные векторы нужной размерности."""

    def __init__(self, model: str = "text-embedding-3-small", dim: int = 1536):
        self.dim = dim  # 1536 для OpenAI, 384 для bge-small

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # В реальности: openai.Embedding.acreate() или sentence-transformers
        return [
            [random.uniform(-0.1, 0.1) for _ in range(self.dim)]
            for _ in texts
        ]