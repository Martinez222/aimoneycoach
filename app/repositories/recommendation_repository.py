from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, allocation: dict, summary: str,
                     risk_score: int, health_score: int) -> Recommendation:
        rec = Recommendation(
            user_id=user_id,
            allocation_json=allocation,
            summary=summary,
            risk_score=risk_score,
            financial_health_score=health_score,
        )
        self.db.add(rec)
        await self.db.flush()
        await self.db.refresh(rec)
        return rec

    async def get_latest(self, user_id: int) -> Recommendation | None:
        result = await self.db.execute(
            select(Recommendation)
            .where(Recommendation.user_id == user_id)
            .order_by(Recommendation.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def delete_by_user_id(self, user_id: int) -> None:
        await self.db.execute(
            delete(Recommendation).where(Recommendation.user_id == user_id)
        )
