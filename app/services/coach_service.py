from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_profile import FinancialProfile
from app.models.recommendation import Recommendation
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.coach_schema import (
    CoachOverviewResponse,
    EmergencyFundResponse,
    FinancialSnapshotResponse,
)
from app.schemas.profile_schema import ProfileCreate
from app.schemas.recommendation_schema import RecommendationResponse
from app.services.ai_service import AIService
from app.services.financial_profile_service import FinancialProfileService
from app.services.recommendation_service import RecommendationService
from app.services.risk_service import RiskService
from app.utils.locale import is_english


class CoachService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.profile_service = FinancialProfileService(db)
        self.recommendation_service = RecommendationService(db)
        self.profile_repo = ProfileRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.chat_repo = ChatRepository(db)
        self.risk_service = RiskService()
        self.ai_service = AIService()

    async def _build_snapshot(
        self,
        profile: FinancialProfile,
        locale: str = "ro",
    ) -> FinancialSnapshotResponse:
        emergency_fund = self.risk_service.get_emergency_fund_status(profile)
        summary = await self.ai_service.generate_financial_summary(
            {
                "monthly_income": profile.monthly_income,
                "monthly_expenses": profile.monthly_expenses,
                "emergency_fund": profile.emergency_fund,
                "emergency_fund_target_months": emergency_fund["target_months"],
                "emergency_fund_target_amount": emergency_fund["target_amount"],
                "savings": profile.savings,
                "debts": profile.debts,
            },
            locale,
        )

        return FinancialSnapshotResponse(
            monthly_income=profile.monthly_income,
            monthly_expenses=profile.monthly_expenses,
            monthly_savings_capacity=self.risk_service.get_monthly_savings_capacity(profile),
            emergency_fund_amount=profile.emergency_fund,
            savings=profile.savings,
            debts=profile.debts,
            risk_profile=profile.risk_profile,
            financial_goals=profile.financial_goals or [],
            risk_score=self.risk_service.calculate_risk_score(profile),
            financial_health_score=self.risk_service.calculate_financial_health_score(profile),
            summary=summary,
            emergency_fund=EmergencyFundResponse(**emergency_fund),
        )

    def _build_next_step(
        self,
        profile: FinancialProfile | None,
        recommendation: Recommendation | None,
        locale: str = "ro",
    ) -> str:
        english = is_english(locale)
        if not profile:
            return (
                "Complete your financial profile to receive your first personalized analysis."
                if english
                else "Completeaza profilul financiar pentru a primi prima analiza personalizata."
            )
        if not recommendation:
            return (
                "Generate your first recommendation to turn the profile into a concrete plan."
                if english
                else "Genereaza prima recomandare pentru a transforma profilul intr-un plan concret."
            )
        return (
            "Your plan is ready. The next useful step is to use the chat for focused questions and adjustments."
            if english
            else "Planul este gata. Urmatorul pas este sa folosesti chat-ul pentru intrebari punctuale si ajustari."
        )

    async def get_overview(self, user: User, locale: str = "ro") -> CoachOverviewResponse:
        profile = await self.profile_service.get_profile(user.id)
        recommendation = await self.recommendation_service.get_latest(user.id)

        snapshot = await self._build_snapshot(profile, locale) if profile else None
        recommendation_response = (
            await self.recommendation_service.build_response(recommendation, locale)
            if recommendation
            else None
        )

        return CoachOverviewResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            profile_complete=profile is not None,
            plan_ready=recommendation is not None,
            ai_enabled=self.ai_service.is_groq_configured(),
            next_step=self._build_next_step(profile, recommendation, locale),
            financial_snapshot=snapshot,
            latest_recommendation=recommendation_response,
        )

    async def create_plan(self, user: User, locale: str = "ro") -> CoachOverviewResponse:
        profile = await self.profile_service.get_profile(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Complete your financial profile before generating the plan."
                    if locale == "en"
                    else "Completeaza profilul financiar inainte sa generezi planul."
                ),
            )

        recommendation = await self.recommendation_service.generate(user.id, locale)
        snapshot = await self._build_snapshot(profile, locale)

        return CoachOverviewResponse(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            profile_complete=True,
            plan_ready=True,
            ai_enabled=self.ai_service.is_groq_configured(),
            next_step=(
                "The plan is ready. You can go straight to the chat for clarifications and next steps."
                if locale == "en"
                else "Planul este gata. Poti merge direct in chat pentru clarificari si pasi urmatori."
            ),
            financial_snapshot=snapshot,
            latest_recommendation=await self.recommendation_service.build_response(
                recommendation,
                locale,
            ),
        )

    async def setup_profile(self, user: User, data: ProfileCreate, locale: str = "ro") -> CoachOverviewResponse:
        await self.profile_service.save_profile(user.id, data)
        return await self.create_plan(user, locale)

    async def reset_user_data(self, user_id: int) -> None:
        await self.chat_repo.delete_by_user_id(user_id)
        await self.recommendation_repo.delete_by_user_id(user_id)
        await self.profile_repo.delete_by_user_id(user_id)
