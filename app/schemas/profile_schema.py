from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ProfileCreate(BaseModel):
    monthly_income: float = Field(gt=0, description="Venitul lunar brut")
    monthly_expenses: float = Field(
        gt=0,
        description="Cheltuielile lunare recurente, fara ratele catre alti creditori",
    )
    monthly_debt_obligations: float = Field(
        default=0.0,
        ge=0,
        description="Rate lunare si alte obligatii recurente de plata catre creditori",
    )
    age: int | None = Field(default=None, ge=18, le=80)
    credit_gender: str | None = Field(default=None, pattern="^(male|female)$")
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
    monthly_debt_obligations: float
    age: int | None = None
    credit_gender: str | None = None
    emergency_fund: float
    savings: float
    debts: float
    risk_profile: str
    financial_goals: List[str]
    created_at: datetime | None = None

    class Config:
        from_attributes = True
