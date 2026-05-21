from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile_repository import ProfileRepository
from app.models.financial_profile import FinancialProfile
from app.schemas.profile_schema import ProfileCreate


class FinancialProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def get_profile(self, user_id: int) -> FinancialProfile | None:
        return await self.repo.get_by_user_id(user_id)

    async def save_profile(self, user_id: int, data: ProfileCreate) -> FinancialProfile:
        return await self.repo.create_or_update(user_id, data.model_dump())