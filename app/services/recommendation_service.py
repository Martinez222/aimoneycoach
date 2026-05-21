from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.repositories.profile_repository import ProfileRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation_schema import RecommendationResponse
from app.services.ai_service import AIService
from app.services.risk_service import RiskService


class RecommendationService:
    """
    Flow: rules compute allocation, AI explains it.
    Never the other way around.
    """

    def __init__(self, db: AsyncSession):
        self.rec_repo = RecommendationRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.ai_service = AIService()
        self.risk_service = RiskService()

    async def generate(self, user_id: int, locale: str = "ro") -> Recommendation:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Financial profile not found. Complete your profile first."
                    if locale == "en"
                    else "Profil financiar negasit. Completeaza profilul mai intai."
                ),
            )

        risk_score = self.risk_service.calculate_risk_score(profile)
        health_score = self.risk_service.calculate_financial_health_score(profile)
        allocation = self.risk_service.get_allocation(profile, risk_score)
        emergency_fund = self.risk_service.get_emergency_fund_status(profile)

        profile_data = {
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "emergency_fund": profile.emergency_fund,
            "emergency_fund_target_months": emergency_fund["target_months"],
            "emergency_fund_target_amount": emergency_fund["target_amount"],
            "savings": profile.savings,
            "debts": profile.debts,
            "risk_profile": profile.risk_profile,
            "financial_goals": profile.financial_goals or [],
        }
        summary = await self.ai_service.generate_recommendations(
            profile_data, allocation, risk_score, health_score, locale
        )

        return await self.rec_repo.create(user_id, allocation, summary, risk_score, health_score)

    async def get_latest(self, user_id: int) -> Recommendation | None:
        return await self.rec_repo.get_latest(user_id)

    async def build_response(
        self,
        recommendation: Recommendation,
        locale: str = "ro",
    ) -> RecommendationResponse:
        profile = await self.profile_repo.get_by_user_id(recommendation.user_id)
        if not profile:
            return RecommendationResponse.from_model(recommendation)

        risk_score = recommendation.risk_score or self.risk_service.calculate_risk_score(profile)
        health_score = (
            recommendation.financial_health_score
            or self.risk_service.calculate_financial_health_score(profile)
        )
        emergency_fund = self.risk_service.get_emergency_fund_status(profile)
        profile_data = {
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "emergency_fund": profile.emergency_fund,
            "emergency_fund_target_months": emergency_fund["target_months"],
            "emergency_fund_target_amount": emergency_fund["target_amount"],
            "savings": profile.savings,
            "debts": profile.debts,
            "risk_profile": profile.risk_profile,
            "financial_goals": profile.financial_goals or [],
        }
        localized_summary = await self.ai_service.generate_recommendations(
            profile_data,
            recommendation.allocation_json or {},
            risk_score,
            health_score,
            locale,
        )

        return RecommendationResponse(
            id=recommendation.id,
            user_id=recommendation.user_id,
            allocation=recommendation.allocation_json or {},
            summary=localized_summary,
            risk_score=risk_score,
            financial_health_score=health_score,
            created_at=recommendation.created_at,
        )
