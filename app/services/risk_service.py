from app.models.financial_profile import FinancialProfile


class RiskService:
    """
    Core financial logic engine.
    Scores and evaluates user financial health using rule-based logic.
    AI only explains - this service decides.
    """

    def get_monthly_debt_obligations(self, profile: FinancialProfile) -> float:
        return max(0.0, getattr(profile, "monthly_debt_obligations", 0.0) or 0.0)

    def get_monthly_required_outflow(self, profile: FinancialProfile) -> float:
        return max(0.0, profile.monthly_expenses + self.get_monthly_debt_obligations(profile))

    def get_monthly_debt_service_ratio(self, profile: FinancialProfile) -> float:
        monthly_income = profile.monthly_income
        obligations = self.get_monthly_debt_obligations(profile)
        return obligations / monthly_income if monthly_income > 0 else 0.0

    def get_emergency_target_months(self, profile: FinancialProfile) -> int:
        monthly_income = profile.monthly_income
        monthly_expenses = self.get_monthly_required_outflow(profile)
        debts = profile.debts
        savings_capacity = monthly_income - monthly_expenses
        savings_rate = savings_capacity / monthly_income if monthly_income > 0 else 0.0
        debt_ratio = self.get_monthly_debt_service_ratio(profile)
        total_debt_ratio = debts / (monthly_income * 12) if monthly_income > 0 else 0.0

        if (
            profile.risk_profile == "conservative"
            or savings_capacity <= 0
            or debt_ratio >= 0.4
            or total_debt_ratio >= 0.8
        ):
            return 9
        if (
            profile.risk_profile == "aggressive"
            and savings_rate >= 0.2
            and debt_ratio <= 0.2
            and total_debt_ratio <= 0.2
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
        monthly_expenses = self.get_monthly_required_outflow(profile)
        emergency_fund = getattr(profile, "emergency_fund", 0.0)
        debts = profile.debts
        debt_obligations = self.get_monthly_debt_obligations(profile)

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
        dti = self.get_monthly_debt_service_ratio(profile)
        leverage_ratio = debts / (monthly_income * 12) if monthly_income > 0 else 0
        if dti == 0 and leverage_ratio == 0:
            score += 10
        elif dti < 0.2 and leverage_ratio < 0.5:
            score += 5
        elif dti < 0.4 and leverage_ratio < 1.0:
            pass  # neutral
        else:
            score -= 20  # high debt

        if debt_obligations >= monthly_income * 0.35:
            score -= 10

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
        monthly_expenses = self.get_monthly_required_outflow(profile)
        emergency_fund = getattr(profile, "emergency_fund", 0.0)
        debts = profile.debts
        debt_obligations = self.get_monthly_debt_obligations(profile)

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
        if debts == 0 and debt_obligations == 0:
            score += 15
        elif debt_obligations <= monthly_income * 0.15 and debts < monthly_income * 3:
            score += 5
        elif debt_obligations >= monthly_income * 0.4 or debts > monthly_income * 12:
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
        return max(0.0, profile.monthly_income - self.get_monthly_required_outflow(profile))

    def get_emergency_fund_status(self, profile: FinancialProfile) -> dict:
        current_amount = getattr(profile, "emergency_fund", 0.0)
        target_months = self.get_emergency_target_months(profile)
        required_outflow = self.get_monthly_required_outflow(profile)
        months = current_amount / required_outflow if required_outflow > 0 else 0
        target = required_outflow * target_months
        shortfall = max(0.0, target - current_amount)
        return {
            "current_months": round(months, 1),
            "target_months": target_months,
            "current_amount": round(current_amount, 2),
            "target_amount": target,
            "shortfall_amount": round(shortfall, 2),
            "is_adequate": months >= target_months,
        }
