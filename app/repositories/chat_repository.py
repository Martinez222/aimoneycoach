from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.simulation import ChatHistory


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, message: str, response: str) -> ChatHistory:
        chat_entry = ChatHistory(user_id=user_id, message=message, response=response)
        self.db.add(chat_entry)
        await self.db.flush()
        await self.db.refresh(chat_entry)
        return chat_entry

    async def get_recent(self, user_id: int, limit: int = 10) -> list[ChatHistory]:
        result = await self.db.execute(
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_by_user_id(self, user_id: int) -> None:
        await self.db.execute(delete(ChatHistory).where(ChatHistory.user_id == user_id))
