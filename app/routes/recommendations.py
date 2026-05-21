from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.recommendation_schema import RecommendationResponse
from app.services.recommendation_service import RecommendationService
from app.utils.locale import normalize_locale

router = APIRouter()


@router.post("/generate", response_model=RecommendationResponse)
async def generate_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Generate AI-powered financial recommendations."""
    locale = normalize_locale(accept_language)
    service = RecommendationService(db)
    recommendation = await service.generate(current_user.id, locale)
    return await service.build_response(recommendation, locale)


@router.get("/latest", response_model=RecommendationResponse)
async def get_latest_recommendation(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Get the user's latest recommendation."""
    locale = normalize_locale(accept_language)
    service = RecommendationService(db)
    recommendation = await service.get_latest(current_user.id)
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No recommendation available"
                if locale == "en"
                else "Nicio recomandare disponibila"
            ),
        )
    return await service.build_response(recommendation, locale)
