from uuid import UUID
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, VectorInput
from typing import List



class QdrantService:
    def __init__(self, client: AsyncQdrantClient, collection: str):
        self.client = client
        self.collection = collection

    async def delete_book(self, book_id: UUID):
        count_result = await self.client.count(
            collection_name=self.collection,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="book_id",
                        match=MatchValue(value=str(book_id)),
                    )
                ]
            ),
        )

        if count_result.count == 0:
            raise ValueError("NotFound")

        await self.client.delete(
            collection_name=self.collection,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="book_id",
                        match=MatchValue(value=str(book_id)),
                    )
                ]
            ),
            wait=True,
        )

    async def get_all_points(self):
        points, _ = await self.client.scroll(
            collection_name=self.collection,
            with_payload=True,
            with_vectors=False,
            limit=999999
        )
        return points

    async def update_book_metadata(self, book_id: UUID, payload: dict):
        book_id_str = str(book_id)

        book_filter = Filter(
            must=[
                FieldCondition(
                    key="book_id",
                    match=MatchValue(value=book_id_str),
                )
            ]
        )

        count_result = await self.client.count(
            collection_name=self.collection,
            count_filter=book_filter,
        )

        if count_result.count == 0:
            raise ValueError("NotFound")


        await self.client.set_payload(
            collection_name=self.collection,
            payload=payload,
            points=book_filter,
            wait=True,
        )

    async def semantic_search_in_book(
            self,
            book_id: UUID,
            query_vector: List[float],
            limit: int = 5,
            score_threshold: float = 0.7,
    ) -> List[dict]:
        # Фильтр: только чанки этой книги
        book_filter = Filter(
            must=[
                FieldCondition(
                    key="book_id",
                    match=MatchValue(value=str(book_id)),
                )
            ]
        )

        # Поиск по вектору с фильтром
        results = await self.client.query_points(
            collection_name=self.collection,
            query=query_vector,
            query_filter=book_filter,
            limit=limit,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )

        # Извлекаем payload из результатов
        chunks = []
        for point in results.points:
            if point.payload:
                chunks.append({
                    "content": point.payload.get("content", ""),
                    "metadata": {
                        k: v for k, v in point.payload.items()
                        if k != "content"
                    }
                })

        return chunks

    async def book_exists(self, book_id: UUID) -> bool:
        count_result = await self.client.count(
            collection_name=self.collection,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="book_id",
                        match=MatchValue(value=str(book_id)),
                    )
                ]
            ),
        )
        return count_result.count > 0