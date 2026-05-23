from pydantic import BaseModel

from app.schemas.recommendation_schema import RecommendationResponse


class EmergencyFundResponse(BaseModel):
    current_months: float
    target_months: int
    current_amount: float
    target_amount: float
    shortfall_amount: float
    is_adequate: bool


class FinancialSnapshotResponse(BaseModel):
    monthly_income: float
    monthly_expenses: float
    age: int | None = None
    credit_gender: str | None = None
    monthly_savings_capacity: float
    emergency_fund_amount: float
    savings: float
    debts: float
    risk_profile: str
    financial_goals: list[str]
    risk_score: int
    financial_health_score: int
    summary: str
    emergency_fund: EmergencyFundResponse


class CoachOverviewResponse(BaseModel):
    user_id: int
    email: str
    full_name: str | None = None
    profile_complete: bool
    plan_ready: bool
    ai_enabled: bool
    next_step: str
    financial_snapshot: FinancialSnapshotResponse | None = None
    latest_recommendation: RecommendationResponse | None = None
