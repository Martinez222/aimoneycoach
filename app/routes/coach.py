from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.coach_schema import CoachOverviewResponse
from app.schemas.goal_schema import GoalPlanRequest, GoalPlanResponse
from app.schemas.profile_schema import ProfileCreate
from app.services.coach_service import CoachService
from app.services.goal_service import GoalService
from app.utils.locale import normalize_locale

router = APIRouter()


@router.get("/overview", response_model=CoachOverviewResponse)
async def get_coach_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Get the current financial coaching overview for the logged-in user."""
    service = CoachService(db)
    return await service.get_overview(current_user, normalize_locale(accept_language))


@router.post("/plan", response_model=CoachOverviewResponse)
async def generate_coach_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Generate or refresh the financial coaching plan for the logged-in user."""
    service = CoachService(db)
    return await service.create_plan(current_user, normalize_locale(accept_language))


@router.post("/setup", response_model=CoachOverviewResponse)
async def setup_coach_profile(
    data: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Save profile data and generate the plan in one step."""
    service = CoachService(db)
    return await service.setup_profile(current_user, data, normalize_locale(accept_language))


@router.post("/goal-plan", response_model=GoalPlanResponse)
async def build_goal_plan(
    data: GoalPlanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Build a personalized goal plan using profile data and current market offers."""
    service = GoalService(db)
    return await service.build_goal_plan(current_user.id, data, normalize_locale(accept_language))


@router.delete("/reset")
async def reset_coach_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    accept_language: str | None = Header(default=None),
):
    """Delete the user's saved profile, recommendations, and chat history while keeping the account."""
    locale = normalize_locale(accept_language)
    service = CoachService(db)
    await service.reset_user_data(current_user.id)
    return {
        "detail": (
            "All saved financial data has been deleted. Your account is still active."
            if locale == "en"
            else "Toate datele financiare salvate au fost sterse. Contul tau ramane activ."
        )
    }
