from app.models.financial_profile import FinancialProfile


class RiskService:
    """
    Core financial logic engine.
    Scores and evaluates user financial health using rule-based logic.
    AI only explains - this service decides.
    """

    def get_emergency_target_months(self, profile: FinancialProfile) -> int:
        monthly_income = profile.monthly_income
        monthly_expenses = profile.monthly_expenses
        debts = profile.debts
        savings_capacity = monthly_income - monthly_expenses
        savings_rate = savings_capacity / monthly_income if monthly_income > 0 else 0.0
        debt_ratio = debts / (monthly_income * 12) if monthly_income > 0 else 0.0

        if (
            profile.risk_profile == "conservative"
            or savings_capacity <= 0
            or debt_ratio >= 0.4
        ):
            return 9
        if (
            profile.risk_profile == "aggressive"
            and savings_rate >= 0.2
            and debt_ratio <= 0.2
        ):
            return 3
        return 6

    def calculate_risk_score(self, profile: FinancialProfile) -> int:
        """
        Returns a risk score 0-100.
        Higher = user can afford more investment risk.
        """
        score = 50  # baseline

        monthly_income = profile.monthly_income
        monthly_expenses = profile.monthly_expenses
        emergency_fund = getattr(profile, "emergency_fund", 0.0)
        debts = profile.debts

        # 1. Savings rate bonus/penalty
        savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
        if savings_rate >= 0.30:
            score += 20
        elif savings_rate >= 0.20:
            score += 10
        elif savings_rate >= 0.10:
            score += 5
        elif savings_rate < 0:
            score -= 25  # spending more than earning

        # 2. Emergency fund check (3-6 months of expenses)
        months_of_emergency = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
        emergency_target_months = self.get_emergency_target_months(profile)
        if months_of_emergency >= emergency_target_months:
            score += 15
        elif months_of_emergency >= 3:
            score += 5
        else:
            score -= 15  # no emergency fund = cannot take risks

        # 3. Debt-to-income ratio
        dti = debts / (monthly_income * 12) if monthly_income > 0 else 0
        if dti == 0:
            score += 10
        elif dti < 0.2:
            score += 5
        elif dti < 0.4:
            pass  # neutral
        else:
            score -= 20  # high debt

        # 4. Risk profile preference adjustment
        if profile.risk_profile == "aggressive":
            score += 10
        elif profile.risk_profile == "conservative":
            score -= 10

        return max(0, min(100, score))

    def calculate_financial_health_score(self, profile: FinancialProfile) -> int:
        """
        Overall financial health 0-100.
        """
        score = 50

        monthly_income = profile.monthly_income
        monthly_expenses = profile.monthly_expenses
        emergency_fund = getattr(profile, "emergency_fund", 0.0)
        debts = profile.debts

        # Savings rate
        savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
        if savings_rate >= 0.20:
            score += 20
        elif savings_rate >= 0.10:
            score += 10
        elif savings_rate < 0:
            score -= 30

        # Emergency fund
        months_covered = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
        emergency_target_months = self.get_emergency_target_months(profile)
        if months_covered >= emergency_target_months:
            score += 15
        elif months_covered >= 3:
            score += 5
        elif months_covered < 1:
            score -= 15

        # Debt burden
        if debts == 0:
            score += 15
        elif debts < monthly_income * 3:
            score += 5
        elif debts > monthly_income * 12:
            score -= 20

        return max(0, min(100, score))

    def get_allocation(self, profile: FinancialProfile, risk_score: int) -> dict:
        """
        Rule-based portfolio allocation.
        AI explains this — it does NOT decide it.
        """
        if risk_score >= 70:
            return {
                "etf_global": 60,
                "bonds": 15,
                "cash": 15,
                "high_risk": 10,
            }
        elif risk_score >= 40:
            return {
                "etf_global": 50,
                "bonds": 25,
                "cash": 20,
                "high_risk": 5,
            }
        else:
            return {
                "etf_global": 30,
                "bonds": 40,
                "cash": 30,
                "high_risk": 0,
            }

    def get_monthly_savings_capacity(self, profile: FinancialProfile) -> float:
        return max(0.0, profile.monthly_income - profile.monthly_expenses)

    def get_emergency_fund_status(self, profile: FinancialProfile) -> dict:
        current_amount = getattr(profile, "emergency_fund", 0.0)
        target_months = self.get_emergency_target_months(profile)
        months = current_amount / profile.monthly_expenses if profile.monthly_expenses > 0 else 0
        target = profile.monthly_expenses * target_months
        shortfall = max(0.0, target - current_amount)
        return {
            "current_months": round(months, 1),
            "target_months": target_months,
            "current_amount": round(current_amount, 2),
            "target_amount": target,
            "shortfall_amount": round(shortfall, 2),
            "is_adequate": months >= target_months,
        }
