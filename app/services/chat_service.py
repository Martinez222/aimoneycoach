from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recommendation import Recommendation
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.chat_schema import ChatHistoryResponse, ChatResponse
from app.services.ai_service import AIService
from app.services.goal_service import GoalService
from app.services.risk_service import RiskService


class ChatService:
    def __init__(self, db: AsyncSession):
        self.chat_repo = ChatRepository(db)
        self.profile_repo = ProfileRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.ai_service = AIService()
        self.goal_service = GoalService(db)
        self.risk_service = RiskService()

    def _build_context(self, user: User, profile, recommendation: Recommendation | None) -> dict:
        if not profile:
            return {
                "has_profile": False,
                "has_recommendation": recommendation is not None,
                "full_name": user.full_name,
                "email": user.email,
            }

        monthly_savings_capacity = self.risk_service.get_monthly_savings_capacity(profile)
        emergency_fund = self.risk_service.get_emergency_fund_status(profile)

        return {
            "has_profile": True,
            "has_recommendation": recommendation is not None,
            "full_name": user.full_name,
            "email": user.email,
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "monthly_debt_obligations": profile.monthly_debt_obligations,
            "monthly_savings_capacity": monthly_savings_capacity,
            "emergency_fund_amount": profile.emergency_fund,
            "emergency_fund_target_months": emergency_fund["target_months"],
            "emergency_fund_target_amount": emergency_fund["target_amount"],
            "savings": profile.savings,
            "debts": profile.debts,
            "risk_profile": profile.risk_profile,
            "financial_goals": profile.financial_goals or [],
            "risk_score": self.risk_service.calculate_risk_score(profile),
            "financial_health_score": self.risk_service.calculate_financial_health_score(profile),
            "emergency_fund_months": emergency_fund["current_months"],
            "recommendation_allocation": recommendation.allocation_json if recommendation else {},
            "recommendation_summary": recommendation.summary if recommendation else None,
        }

    async def ask(self, user: User, message: str, locale: str = "ro") -> ChatResponse:
        profile = await self.profile_repo.get_by_user_id(user.id)
        recommendation = await self.recommendation_repo.get_latest(user.id)
        context = self._build_context(user, profile, recommendation)

        goal_request = self.goal_service.extract_goal_request(message, locale)
        if goal_request and profile:
            goal_plan = await self.goal_service.build_goal_plan(user.id, goal_request, locale)
            response_text = self.goal_service.render_chat_goal_plan(goal_plan, locale)
        else:
            response_text = await self.ai_service.chat_response(message, context, locale)

        await self.chat_repo.create(user.id, message, response_text)

        return ChatResponse(
            response=response_text,
            used_ai_fallback=not self.ai_service.is_groq_configured(),
            has_profile_context=profile is not None,
            has_recommendation_context=recommendation is not None,
        )

    async def get_history(self, user_id: int, limit: int = 10) -> list[ChatHistoryResponse]:
        history = await self.chat_repo.get_recent(user_id, limit=limit)
        return [
            ChatHistoryResponse(
                message=item.message,
                response=item.response,
                created_at=item.created_at,
            )
            for item in history
        ]
