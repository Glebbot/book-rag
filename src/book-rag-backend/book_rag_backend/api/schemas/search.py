from pydantic import BaseModel, Field, field_validator
from typing import List
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content can't be empty")
        return v.strip()


class SearchRequest(BaseModel):
    messages: List[Message] = Field(..., min_length=1)

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v):
        if not v:
            raise ValueError("Messages list can't be empty")
        return v


class SearchResponse(BaseModel):
    messages: List[Message]


class ErrorResponse(BaseModel):
    errorCode: str
    userMessage: str