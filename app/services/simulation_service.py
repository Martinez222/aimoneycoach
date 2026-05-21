import math
from app.schemas.simulation_schema import (
    CompoundInterestRequest, CompoundInterestResponse,
    FireCalculatorRequest, FireCalculatorResponse
)


class SimulationService:
    """
    Pure financial math. No AI needed here.
    """

    def compound_interest(self, req: CompoundInterestRequest) -> CompoundInterestResponse:
        rate = req.annual_rate / 100 / 12  # monthly rate
        months = req.years * 12
        amount = req.initial_amount
        total_contributed = req.initial_amount
        yearly_breakdown = []

        for month in range(1, months + 1):
            amount = amount * (1 + rate) + req.monthly_contribution
            total_contributed += req.monthly_contribution
            if month % 12 == 0:
                yearly_breakdown.append({
                    "year": month // 12,
                    "amount": round(amount, 2),
                    "contributed": round(total_contributed, 2),
                    "interest": round(amount - total_contributed, 2),
                })

        return CompoundInterestResponse(
            final_amount=round(amount, 2),
            total_contributed=round(total_contributed, 2),
            total_interest=round(amount - total_contributed, 2),
            yearly_breakdown=yearly_breakdown,
        )

    def fire_calculator(self, req: FireCalculatorRequest) -> FireCalculatorResponse:
        """
        FIRE = Financial Independence, Retire Early
        FIRE Number = Annual Expenses / Safe Withdrawal Rate
        """
        annual_expenses = req.monthly_expenses * 12
        fire_number = annual_expenses / (req.safe_withdrawal_rate / 100)
        monthly_rate = req.annual_return / 100 / 12

        amount = req.current_savings
        months = 0
        yearly_breakdown = []
        max_months = 50 * 12

        while amount < fire_number and months < max_months:
            amount = amount * (1 + monthly_rate) + req.monthly_savings
            months += 1
            if months % 12 == 0:
                yearly_breakdown.append({
                    "year": months // 12,
                    "amount": round(amount, 2),
                    "fire_number": round(fire_number, 2),
                    "progress_pct": round(min(100, amount / fire_number * 100), 1),
                })

        years_to_fire = months / 12

        return FireCalculatorResponse(
            fire_number=round(fire_number, 2),
            years_to_fire=round(years_to_fire, 1),
            monthly_passive_income=round(req.monthly_expenses, 2),
            yearly_breakdown=yearly_breakdown[:30],  # cap at 30 years display
        )

    def house_savings(self, target_amount: float, monthly_savings: float,
                      current_savings: float, annual_rate: float = 3.0) -> dict:
        rate = annual_rate / 100 / 12
        amount = current_savings
        months = 0
        max_months = 30 * 12

        while amount < target_amount and months < max_months:
            amount = amount * (1 + rate) + monthly_savings
            months += 1

        return {
            "target_amount": target_amount,
            "months_needed": months,
            "years_needed": round(months / 12, 1),
            "final_amount": round(amount, 2),
        }

    def inflation_impact(self, amount: float, years: int, inflation_rate: float = 5.0) -> dict:
        future_value = amount * math.pow(1 + inflation_rate / 100, years)
        purchasing_power_loss = future_value - amount
        real_value_today = amount / math.pow(1 + inflation_rate / 100, years)

        return {
            "original_amount": amount,
            "years": years,
            "inflation_rate": inflation_rate,
            "future_nominal": round(future_value, 2),
            "real_value_today": round(real_value_today, 2),
            "purchasing_power_loss_pct": round((1 - real_value_today / amount) * 100, 1),
        }