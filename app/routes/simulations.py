from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.simulation_schema import (
    CompoundInterestRequest, CompoundInterestResponse,
    FireCalculatorRequest, FireCalculatorResponse,
)
from app.services.simulation_service import SimulationService

router = APIRouter()


@router.post("/compound-interest", response_model=CompoundInterestResponse)
async def compound_interest(
    req: CompoundInterestRequest,
    current_user: User = Depends(get_current_user),
):
    svc = SimulationService()
    return svc.compound_interest(req)


@router.post("/fire", response_model=FireCalculatorResponse)
async def fire_calculator(
    req: FireCalculatorRequest,
    current_user: User = Depends(get_current_user),
):
    svc = SimulationService()
    return svc.fire_calculator(req)


class HouseSavingsRequest(BaseModel):
    target_amount: float = Field(gt=0)
    monthly_savings: float = Field(gt=0)
    current_savings: float = Field(default=0.0, ge=0)
    annual_rate: float = Field(default=3.0, ge=0, le=20)


@router.post("/house-savings")
async def house_savings(
    req: HouseSavingsRequest,
    current_user: User = Depends(get_current_user),
):
    svc = SimulationService()
    return svc.house_savings(
        req.target_amount, req.monthly_savings, req.current_savings, req.annual_rate
    )


class InflationRequest(BaseModel):
    amount: float = Field(gt=0)
    years: int = Field(gt=0, le=50)
    inflation_rate: float = Field(default=5.0, ge=0, le=30)


@router.post("/inflation-impact")
async def inflation_impact(
    req: InflationRequest,
    current_user: User = Depends(get_current_user),
):
    svc = SimulationService()
    return svc.inflation_impact(req.amount, req.years, req.inflation_rate)