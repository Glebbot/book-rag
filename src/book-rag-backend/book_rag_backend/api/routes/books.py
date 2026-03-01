from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from ..schemas.books import BooksListResponse, BookUpdateRequest
from ..dependencies import get_book_service
from ...services.books import BookService
from uuid import UUID

router = APIRouter(prefix="/books", tags=["books"])


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service)
):
    try:
        await service.delete_book(book_id)
        return {}  # 204 No Content с пустым телом
    except ValueError:
        return JSONResponse(
            status_code=404,
            content={"errorCode": "NotFound", "userMessage": "Book not found"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"errorCode": "Exception", "userMessage": "Internal server error"},
        )


@router.get("", response_model=BooksListResponse)
async def get_books(service: BookService = Depends(get_book_service)):
    try:
        books = await service.list_books()
        return {"books": books}
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"errorCode": "Exception", "userMessage": "Internal server error"},
        )


@router.patch("/{book_id}", status_code=200)
async def update_book(
    book_id: UUID,
    request: BookUpdateRequest,
    service: BookService = Depends(get_book_service),
):
    update_payload = request.model_dump(exclude_none=True)

    if not update_payload:
        return JSONResponse(
            status_code=304,
            content={"errorCode": "NotModified", "userMessage": "No fields provided"},
        )

    try:
        await service.update_book(book_id, update_payload)
        return {"status": "updated"}  # 200 OK
    except ValueError:
        return JSONResponse(
            status_code=404,
            content={"errorCode": "NotFound", "userMessage": "Book not found"},
        )
    except TypeError:
        return JSONResponse(
            status_code=422,
            content={"errorCode": "NotSupportedFormat", "userMessage": "format is not supported"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"errorCode": "Exception", "userMessage": "Internal server error"},
        )


@router.post("", status_code=201)
async def create_book(
    file: UploadFile,
    service: BookService = Depends(get_book_service),
):
    try:
        book_id = await service.create_book(file)
        return {"book_id": str(book_id)}
    except TypeError:
        return JSONResponse(
            status_code=422,
            content={"errorCode": "NotSupportedFormat", "userMessage": "format is not supported"},
        )
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"errorCode": "ValidationError", "userMessage": "Bad file"},
        )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"errorCode": "Exception", "userMessage": "Internal server error"},
        )