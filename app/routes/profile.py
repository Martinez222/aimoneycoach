from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.profile_schema import ProfileCreate, ProfileResponse
from app.services.financial_profile_service import FinancialProfileService
from app.utils.locale import normalize_locale

router = APIRouter()


@router.post("/", response_model=ProfileResponse)
async def save_profile(
    profile: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save or update user's financial profile."""
    service = FinancialProfileService(db)
    return await service.save_profile(current_user.id, profile)


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Get user's financial profile."""
    locale = normalize_locale(accept_language)
    service = FinancialProfileService(db)
    profile = await service.get_profile(current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found" if locale == "en" else "Profil financiar negasit",
        )
    return profile
