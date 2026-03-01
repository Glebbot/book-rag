from uuid import UUID
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue


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