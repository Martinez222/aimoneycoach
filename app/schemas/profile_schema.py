from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ProfileCreate(BaseModel):
    monthly_income: float = Field(gt=0, description="Venitul lunar brut")
    monthly_expenses: float = Field(gt=0, description="Cheltuielile lunare totale")
    emergency_fund: float = Field(default=0.0, ge=0)
    savings: float = Field(default=0.0, ge=0)
    debts: float = Field(default=0.0, ge=0)
    risk_profile: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$")
    financial_goals: List[str] = Field(default=[], description="Ex: house, retirement, emergency")


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    monthly_income: float
    monthly_expenses: float
    emergency_fund: float
    savings: float
    debts: float
    risk_profile: str
    financial_goals: List[str]
    created_at: datetime | None = None

    class Config:
        from_attributes = True
