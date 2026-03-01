from uuid import UUID, uuid4
from fastapi import UploadFile
from .qdrant import QdrantService


class BookService:

    def __init__(self, qdrant: QdrantService, parser, splitter, embeddings):
        self.qdrant = qdrant
        self.parser = parser
        self.splitter = splitter
        self.embeddings = embeddings

    async def delete_book(self, book_id: UUID):
        await self.qdrant.delete_book(book_id)

    async def list_books(self):
        points = await self.qdrant.get_all_points()

        books = {}
        for p in points:
            payload = p.payload
            book_id = UUID(payload["book_id"])
            if book_id not in books:
                books[book_id] = {
                    "id": book_id,
                    "name": payload.get("name"),
                    "year": payload.get("year"),
                    "genres": payload.get("genres"),
                    "author": payload.get("author"),
                }

        return list(books.values())

    async def update_book(self, book_id: UUID, update_payload: dict):
        if not update_payload:
            raise ValueError("NotModified")

        await self.qdrant.update_book_metadata(book_id, update_payload)

    async def create_book(self, file: UploadFile) -> UUID:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise TypeError("NotSupportedFormat")

        try:
            content = await file.read()
            if not content or len(content) == 0:
                raise ValueError("BadFile")

            text = self.parser.parse_pdf(content)
            if not text or not text.strip():
                raise ValueError("BadFile")
        except ValueError:
            raise
        except Exception:
            raise ValueError("BadFile")

        book_id = uuid4()
        name = file.filename.rsplit(".", 1)[0]

        chunks = self.splitter.split(text)
        if not chunks:
            raise ValueError("BadFile")

        vectors = await self.embeddings.embed_batch(chunks)

        points = []
        for chunk, vector in zip(chunks, vectors):
            points.append(
                {
                    "id": str(uuid4()),
                    "vector": vector,
                    "payload": {
                        "content": chunk,
                        "book_id": str(book_id),
                        "name": name,
                        "author": None,
                        "year": None,
                        "genres": None,
                    },
                }
            )

        await self.qdrant.client.upsert(
            collection_name=self.qdrant.collection,
            points=points,
        )

        return book_id