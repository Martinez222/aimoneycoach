from datetime import datetime

from pydantic import BaseModel


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    used_ai_fallback: bool = False
    has_profile_context: bool = False
    has_recommendation_context: bool = False


class ChatHistoryResponse(BaseModel):
    message: str
    response: str
    created_at: datetime | None = None
