from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class ErrorResponse(BaseModel):
    errorCode: str
    userMessage: str


class BookShort(BaseModel):
    id: UUID
    name: str
    year: Optional[int] = None
    genres: Optional[List[str]] = None
    author: Optional[str] = None


class BooksListResponse(BaseModel):
    books: List[BookShort]


class BookUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = None
    genres: Optional[List[str]] = None
    author: Optional[str] = Field(None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name can't be empty")
        return v

    @field_validator("author")
    @classmethod
    def validate_author(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Author can't be empty")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v is not None and (v < 0 or v > datetime.now().year):
            raise ValueError(f"Invalid year. Must be between 0 and {datetime.now().year}")
        return v

    @field_validator("genres")
    @classmethod
    def validate_genres(cls, v):
        if v is None:
            return v

        if not isinstance(v, list):
            raise ValueError("Genres must be a list")

        validated_genres = []
        for genre in v:
            if not isinstance(genre, str):
                raise ValueError("Each genre must be a string")

            stripped = genre.strip()
            if not stripped:
                raise ValueError("Genre can't be empty")

            if len(stripped) > 100:
                raise ValueError("Genre can't be longer than 100 characters")

            validated_genres.append(stripped)

        return validated_genres