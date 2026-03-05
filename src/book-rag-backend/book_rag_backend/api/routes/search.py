from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from uuid import UUID

from book_rag_backend.api.schemas.search import SearchRequest, SearchResponse, Message
from book_rag_backend.api.dependencies import get_rag_service
from book_rag_backend.services.rag import RAGService

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/book/{book_id}", response_model=SearchResponse, status_code=200)
async def search_in_book(
        book_id: UUID,
        request: SearchRequest,
        service: RAGService = Depends(get_rag_service),
):
    try:
        messages_dict = [msg.model_dump() for msg in request.messages]

        updated_messages = await service.search_in_book(
            book_id=book_id,
            messages=messages_dict,
        )

        return SearchResponse(
            messages=[
                Message(role=m["role"], content=m["content"])
                for m in updated_messages
            ]
        )

    except ValueError as e:
        error_msg = str(e)

        if error_msg == "NotFound":
            return JSONResponse(
                status_code=404,
                content={"errorCode": "NotFound", "userMessage": "Book not found"},
            )

        if error_msg == "OutOfContext":
            return JSONResponse(
                status_code=413,
                content={
                    "errorCode": "OutOfContext",
                    "userMessage": "prompt is too long (max 200000 tokens)",
                },
            )

        return JSONResponse(
            status_code=400,
            content={"errorCode": "ValidationError", "userMessage": error_msg},
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"errorCode": "Exception", "userMessage": "Internal server error"},
        )