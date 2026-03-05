from fastembed import TextEmbedding


class EmbeddingsService:

    def __init__(self, model: TextEmbedding):
        self.model = model

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = list(self.model.embed(texts, batch_size=20))
        return [emb.tolist() for emb in embeddings]

    def embed(self, text: str) -> list[float]:
        embeddings = list(self.model.embed(text, batch_size=20))
        return [emb.tolist() for emb in embeddings][0]