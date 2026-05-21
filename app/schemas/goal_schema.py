from datetime import datetime

from pydantic import BaseModel, Field


class GoalPlanRequest(BaseModel):
    goal_name: str = Field(min_length=2, max_length=80)
    target_amount: float = Field(gt=0)
    target_currency: str = Field(default="RON", pattern="^(RON|EUR)$")
    target_months: int = Field(ge=1, le=120)
    allow_credit_gap: bool = True
    extra_monthly_savings: float = Field(default=0.0, ge=0)


class MarketOfferResponse(BaseModel):
    category: str
    provider: str
    product_name: str
    suitability: str
    source_url: str
    source_name: str
    retrieved_at: datetime
    annual_rate_percent: float | None = None
    dae_percent: float | None = None
    term_months: int | None = None
    minimum_amount: float | None = None
    indicative_monthly_payment: float | None = None
    indicative_total_value: float | None = None
    indicative_price: float | None = None
    currency: str = "RON"
    offer_type: str | None = None
    bank_rank: int | None = None
    maximum_amount: float | None = None
    requires_property_collateral: bool | None = None
    annual_cost_percent: float | None = None
    transaction_cost_percent: float | None = None
    fx_conversion_cost_percent: float | None = None
    subscription_fee_percent: float | None = None
    redemption_fee_percent: float | None = None
    custody_fee_percent: float | None = None
    cost_summary: str | None = None
    note: str


class GoalAchievementResponse(BaseModel):
    score: int
    label: str
    summary: str
    color: str


class GoalPieSliceResponse(BaseModel):
    key: str
    label: str
    value: float
    color: str


class GoalPlanVariantResponse(BaseModel):
    variant_id: str
    title: str
    subtitle: str
    monthly_contribution: float
    emergency_months_kept: int
    projected_total: float
    funding_gap: float
    feasible_without_credit: bool
    can_hit_target: bool
    estimated_completion_months: int
    uses_credit: bool
    primary_instrument: str
    summary: str
    color: str
    is_recommended: bool = False
    achievement: GoalAchievementResponse


class GoalPlanResponse(BaseModel):
    goal_name: str
    target_amount: float
    requested_target_amount: float | None = None
    requested_target_currency: str | None = None
    reference_fx_rate: float | None = None
    target_months: int
    monthly_savings_capacity: float
    effective_monthly_contribution: float
    emergency_fund_to_keep: float
    available_now_for_goal: float
    projected_savings_by_deadline: float
    funding_gap: float
    feasible_without_credit: bool
    strategy_summary: str
    next_actions: list[str]
    achievement: GoalAchievementResponse
    objective_pie: list[GoalPieSliceResponse]
    plan_variants: list[GoalPlanVariantResponse]
    recommended_variant_id: str
    simulator_extra_monthly_savings: float
    simulator_max_extra_monthly_savings: float
    simulator_step: float
    loan_product_family: str | None = None
    loan_product_family_label: str | None = None
    loan_market_scope: list[str] = []
    safe_saving_offers: list[MarketOfferResponse]
    investment_options: list[MarketOfferResponse]
    broker_options: list[MarketOfferResponse] = []
    loan_options: list[MarketOfferResponse]
