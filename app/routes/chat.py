from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat_schema import ChatHistoryResponse, ChatMessage, ChatResponse
from app.services.chat_service import ChatService
from app.utils.locale import normalize_locale

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_financial_advisor(
    msg: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Ask the financial coach a question using profile and recommendation context."""
    service = ChatService(db)
    return await service.ask(current_user, msg.message, normalize_locale(accept_language))


@router.get("/history", response_model=list[ChatHistoryResponse])
async def get_chat_history(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest chat exchanges for the logged-in user."""
    service = ChatService(db)
    return await service.get_history(current_user.id, limit=limit)
