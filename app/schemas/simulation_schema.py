from pydantic import BaseModel, Field
from typing import List, Dict


class CompoundInterestRequest(BaseModel):
    monthly_contribution: float = Field(gt=0)
    years: int = Field(gt=0, le=50)
    annual_rate: float = Field(gt=0, le=50, description="Rata anuala in procente, ex: 7.5")
    initial_amount: float = Field(default=0.0, ge=0)


class CompoundInterestResponse(BaseModel):
    final_amount: float
    total_contributed: float
    total_interest: float
    yearly_breakdown: List[Dict[str, float]]


class FireCalculatorRequest(BaseModel):
    monthly_expenses: float = Field(gt=0)
    current_savings: float = Field(default=0.0, ge=0)
    monthly_savings: float = Field(gt=0)
    annual_return: float = Field(default=7.0)
    safe_withdrawal_rate: float = Field(default=4.0)


class FireCalculatorResponse(BaseModel):
    fire_number: float
    years_to_fire: float
    monthly_passive_income: float
    yearly_breakdown: List[Dict[str, float]]