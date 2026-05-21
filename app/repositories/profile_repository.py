from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_profile import FinancialProfile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> FinancialProfile | None:
        result = await self.db.execute(
            select(FinancialProfile).where(FinancialProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_or_update(self, user_id: int, data: dict) -> FinancialProfile:
        existing = await self.get_by_user_id(user_id)
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        else:
            profile = FinancialProfile(user_id=user_id, **data)
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)
            return profile

    async def delete_by_user_id(self, user_id: int) -> None:
        await self.db.execute(
            delete(FinancialProfile).where(FinancialProfile.user_id == user_id)
        )
