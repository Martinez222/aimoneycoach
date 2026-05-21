import re
from dataclasses import dataclass
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.profile_repository import ProfileRepository
from app.schemas.goal_schema import (
    GoalAchievementResponse,
    GoalPieSliceResponse,
    GoalPlanRequest,
    GoalPlanResponse,
    GoalPlanVariantResponse,
)
from app.services.market_offer_service import MarketOfferService
from app.services.risk_service import RiskService
from app.utils.locale import is_english


@dataclass
class ScenarioMetrics:
    monthly_contribution: float
    emergency_months_kept: int
    emergency_target: float
    emergency_shortfall: float
    available_now: float
    projected_total: float
    funding_gap: float
    feasible_without_credit: bool
    uses_credit: bool
    can_hit_target: bool
    estimated_completion_months: int


@dataclass
class VariantConfig:
    variant_id: str
    monthly_multiplier: float
    emergency_months_kept: int
    allows_credit: bool
    color: str


class GoalService:
    def __init__(self, db: AsyncSession):
        self.profile_repo = ProfileRepository(db)
        self.risk_service = RiskService()
        self.market_offer_service = MarketOfferService()

    def _loan_family_label(self, loan_family: str | None, locale: str = "ro") -> str | None:
        if not loan_family:
            return None
        english = is_english(locale)
        mapping = {
            "personal_unsecured_loan": (
                "Personal loan" if english else "Credit de nevoi personale"
            ),
            "secured_personal_loan": (
                "Secured personal loan" if english else "Credit de nevoi personale cu ipoteca"
            ),
            "mortgage": (
                "Mortgage / home loan" if english else "Credit ipotecar / imobiliar"
            ),
        }
        return mapping.get(loan_family)

    def _parse_amount(self, raw_amount: str) -> float:
        cleaned = raw_amount.strip().replace(" ", "")
        if "," in cleaned and "." in cleaned:
            if cleaned.rfind(",") > cleaned.rfind("."):
                cleaned = cleaned.replace(".", "").replace(",", ".")
            else:
                cleaned = cleaned.replace(",", "")
        elif cleaned.count(",") == 1 and len(cleaned.split(",")[-1]) in {1, 2}:
            cleaned = cleaned.replace(",", ".")
        elif cleaned.count(".") == 1 and len(cleaned.split(".")[-1]) in {1, 2}:
            pass
        else:
            cleaned = cleaned.replace(",", "").replace(".", "")
        return float(cleaned)

    def _build_simulator_max(self, monthly_income: float, monthly_capacity: float) -> float:
        raw_max = max(500.0, monthly_capacity * 1.5, monthly_income * 0.25)
        rounded = ceil(raw_max / 100) * 100
        return float(min(5000.0, rounded))

    def _compute_scenario(
        self,
        monthly_expenses: float,
        goal_savings: float,
        emergency_fund: float,
        target_amount: float,
        target_months: int,
        monthly_contribution: float,
        emergency_months_kept: int,
        allows_credit: bool,
        has_loan_options: bool,
    ) -> ScenarioMetrics:
        emergency_target = monthly_expenses * emergency_months_kept
        emergency_shortfall = max(0.0, emergency_target - emergency_fund)
        available_now = max(0.0, goal_savings - emergency_shortfall)
        remaining_emergency_shortfall = max(0.0, emergency_shortfall - goal_savings)

        if monthly_contribution <= 0:
            months_reserved_for_emergency = target_months if remaining_emergency_shortfall > 0 else 0
        else:
            months_reserved_for_emergency = ceil(remaining_emergency_shortfall / monthly_contribution)

        months_for_goal = max(0, target_months - months_reserved_for_emergency)
        projected_total = available_now + monthly_contribution * months_for_goal
        funding_gap = max(0.0, target_amount - projected_total)
        feasible_without_credit = funding_gap <= 0.01
        uses_credit = allows_credit and funding_gap > 0.01
        can_hit_target = feasible_without_credit or (uses_credit and has_loan_options)

        remaining_after_available = max(0.0, target_amount - available_now)
        if remaining_after_available <= 0:
            estimated_completion_months = 0
        elif monthly_contribution <= 0:
            estimated_completion_months = min(120, target_months + 60)
        else:
            estimated_completion_months = months_reserved_for_emergency + ceil(
                remaining_after_available / monthly_contribution
            )

        return ScenarioMetrics(
            monthly_contribution=monthly_contribution,
            emergency_months_kept=emergency_months_kept,
            emergency_target=emergency_target,
            emergency_shortfall=emergency_shortfall,
            available_now=available_now,
            projected_total=projected_total,
            funding_gap=funding_gap,
            feasible_without_credit=feasible_without_credit,
            uses_credit=uses_credit,
            can_hit_target=can_hit_target,
            estimated_completion_months=estimated_completion_months,
        )

    def _build_achievement(
        self,
        target_amount: float,
        target_months: int,
        scenario: ScenarioMetrics,
        emergency_months_current: float,
        debt_ratio: float,
        locale: str,
    ) -> GoalAchievementResponse:
        coverage = scenario.projected_total / target_amount if target_amount > 0 else 0.0
        score = coverage * 70

        if scenario.feasible_without_credit:
            score += 12
        elif scenario.can_hit_target and scenario.uses_credit:
            score += 6

        if emergency_months_current >= 3:
            score += 10
        elif emergency_months_current >= 1:
            score += 4
        else:
            score -= 10

        if debt_ratio == 0:
            score += 6
        elif debt_ratio < 0.2:
            score += 2
        elif debt_ratio > 0.4:
            score -= 8

        if target_months >= 24:
            score += 3

        if scenario.uses_credit and not scenario.feasible_without_credit:
            score -= 5

        score = max(8, min(99, round(score)))
        english = is_english(locale)

        if scenario.can_hit_target and scenario.uses_credit and not scenario.feasible_without_credit:
            label = "Achievable with financing" if english else "Realizabil cu finantare"
            summary = (
                "The target can still be hit on time, but only if you accept financing for the remaining gap."
                if english
                else "Obiectivul poate fi atins la termen, dar doar daca accepti finantare pentru diferenta ramasa."
            )
            color = "#b7791f"
        elif score >= 85:
            label = "Very achievable" if english else "Foarte realizabil"
            summary = (
                "At the current pace, the target looks solid and does not require major compromises."
                if english
                else "La ritmul actual, obiectivul arata solid si nu cere compromisuri mari."
            )
            color = "#2c7a4b"
        elif score >= 70:
            label = "Achievable" if english else "Realizabil"
            summary = (
                "The target is realistic, but it still needs monthly discipline."
                if english
                else "Obiectivul este realist, dar cere disciplina lunara."
            )
            color = "#2f7a78"
        elif score >= 55:
            label = "Tight" if english else "La limita"
            summary = (
                "The target is possible, but it would benefit from a higher monthly effort or more time."
                if english
                else "Obiectivul este posibil, dar ar beneficia de un efort lunar mai mare sau de mai mult timp."
            )
            color = "#c68a18"
        else:
            label = "Risky" if english else "Riscant"
            summary = (
                "The target is aggressive for the current situation and needs visible adjustments."
                if english
                else "Obiectivul este agresiv pentru situatia actuala si are nevoie de ajustari vizibile."
            )
            color = "#b94a48"

        return GoalAchievementResponse(
            score=score,
            label=label,
            summary=summary,
            color=color,
        )

    def _build_objective_pie(
        self,
        goal_name: str,
        target_amount: float,
        emergency_target: float,
        debts: float,
        effective_monthly_contribution: float,
        target_months: int,
        goals: list[str],
        locale: str,
    ) -> list[GoalPieSliceResponse]:
        english = is_english(locale)
        slices: list[GoalPieSliceResponse] = [
            GoalPieSliceResponse(
                key="goal_now",
                label=goal_name if goal_name else ("Current goal" if english else "Obiectiv curent"),
                value=round(target_amount, 2),
                color="#d48c32",
            ),
            GoalPieSliceResponse(
                key="emergency_fund",
                label="Emergency buffer" if english else "Fond de urgenta",
                value=round(emergency_target, 2),
                color="#2f7a78",
            ),
        ]

        if debts > 0:
            slices.append(
                GoalPieSliceResponse(
                    key="debt_cleanup",
                    label="Debt cleanup" if english else "Reducere datorii",
                    value=round(debts, 2),
                    color="#b94a48",
                )
            )

        normalized_goals = " ".join(goal.lower() for goal in goals)
        if target_months >= 12 or "invest" in normalized_goals:
            slices.append(
                GoalPieSliceResponse(
                    key="future_investing",
                    label="Future investing" if english else "Investitii viitoare",
                    value=round(max(effective_monthly_contribution * (12 if target_months >= 24 else 6), 0.0), 2),
                    color="#5168b8",
                )
            )

        return [item for item in slices if item.value > 0]

    def _variant_title(self, variant_id: str, locale: str) -> tuple[str, str]:
        english = is_english(locale)
        mapping = {
            "prudent": (
                ("Prudent", "Maximum buffer protection") if english else ("Prudenta", "Protectie maxima pentru buffer")
            ),
            "balanced": (
                ("Balanced", "Healthy mix of speed and safety") if english else ("Echilibrata", "Mix sanatos intre viteza si siguranta")
            ),
            "fast": (
                ("Fast", "Higher push toward the deadline") if english else ("Rapida", "Impuls mai mare spre termen")
            ),
        }
        return mapping[variant_id]

    def _choose_primary_instrument(
        self,
        variant_id: str,
        target_months: int,
        safe_saving_offers,
        investment_options,
        loan_options,
        locale: str,
        uses_credit: bool,
    ) -> str:
        english = is_english(locale)
        best_safe = safe_saving_offers[0].product_name if safe_saving_offers else None
        best_fund = next((offer.product_name for offer in investment_options if offer.category != "stock"), None)
        best_loan = loan_options[0].product_name if loan_options else None

        if variant_id == "prudent":
            return best_safe or ("Safe deposits" if english else "Depozite sigure")
        if variant_id == "balanced":
            if target_months >= 12 and best_fund:
                return best_fund
            return best_safe or ("Government securities" if english else "Titluri de stat")
        if uses_credit and best_loan:
            return best_loan
        if target_months >= 24 and best_fund:
            return best_fund
        return best_safe or ("Diversified saving" if english else "Economisire diversificata")

    def _build_variant_summary(
        self,
        variant_id: str,
        primary_instrument: str,
        scenario: ScenarioMetrics,
        locale: str,
    ) -> str:
        english = is_english(locale)
        if variant_id == "prudent":
            return (
                f"This version keeps a larger cash cushion and leans first on {primary_instrument}."
                if english
                else f"Aceasta varianta pastreaza un buffer de siguranta mai mare si se bazeaza in primul rand pe {primary_instrument}."
            )
        if variant_id == "balanced":
            return (
                f"This version follows the current target without pushing the budget too hard and keeps {primary_instrument} in the center."
                if english
                else f"Aceasta varianta urmareste termenul actual fara sa forteze prea mult bugetul si pastreaza {primary_instrument} in centru."
            )
        if scenario.uses_credit and scenario.funding_gap > 0:
            return (
                f"This version pushes harder on monthly saving and can bridge the difference with {primary_instrument}."
                if english
                else f"Aceasta varianta forteaza economisirea lunara si poate acoperi diferenta cu {primary_instrument}."
            )
        return (
            f"This version accelerates the monthly rhythm and leans on {primary_instrument} to move faster."
            if english
            else f"Aceasta varianta accelereaza ritmul lunar si se sprijina pe {primary_instrument} pentru a merge mai repede."
        )

    def _build_plan_variants(
        self,
        monthly_income: float,
        monthly_expenses: float,
        emergency_fund: float,
        savings: float,
        debts: float,
        target_months: int,
        target_amount: float,
        effective_monthly_contribution: float,
        safe_saving_offers,
        investment_options,
        loan_options,
        allow_credit_gap: bool,
        emergency_target_months: int,
        locale: str,
    ) -> tuple[list[GoalPlanVariantResponse], str]:
        configs = [
            VariantConfig("prudent", 0.85, min(9, max(6, emergency_target_months + 3)), False, "#2c7a4b"),
            VariantConfig("balanced", 1.0, emergency_target_months, False, "#2f7a78"),
            VariantConfig("fast", 1.15, max(3, emergency_target_months - 3), allow_credit_gap, "#b7791f"),
        ]

        emergency_months_current = emergency_fund / monthly_expenses if monthly_expenses else 0.0
        debt_ratio = debts / max(monthly_income * 12, 1.0)
        variants: list[GoalPlanVariantResponse] = []

        for config in configs:
            scenario = self._compute_scenario(
                monthly_expenses=monthly_expenses,
                goal_savings=savings,
                emergency_fund=emergency_fund,
                target_amount=target_amount,
                target_months=target_months,
                monthly_contribution=round(max(0.0, effective_monthly_contribution * config.monthly_multiplier), 2),
                emergency_months_kept=config.emergency_months_kept,
                allows_credit=config.allows_credit,
                has_loan_options=bool(loan_options),
            )
            achievement = self._build_achievement(
                target_amount=target_amount,
                target_months=target_months,
                scenario=scenario,
                emergency_months_current=emergency_months_current,
                debt_ratio=debt_ratio,
                locale=locale,
            )
            title, subtitle = self._variant_title(config.variant_id, locale)
            primary_instrument = self._choose_primary_instrument(
                variant_id=config.variant_id,
                target_months=target_months,
                safe_saving_offers=safe_saving_offers,
                investment_options=investment_options,
                loan_options=loan_options,
                locale=locale,
                uses_credit=scenario.uses_credit,
            )
            summary = self._build_variant_summary(
                variant_id=config.variant_id,
                primary_instrument=primary_instrument,
                scenario=scenario,
                locale=locale,
            )
            variants.append(
                GoalPlanVariantResponse(
                    variant_id=config.variant_id,
                    title=title,
                    subtitle=subtitle,
                    monthly_contribution=round(scenario.monthly_contribution, 2),
                    emergency_months_kept=config.emergency_months_kept,
                    projected_total=round(scenario.projected_total, 2),
                    funding_gap=round(scenario.funding_gap, 2),
                    feasible_without_credit=scenario.feasible_without_credit,
                    can_hit_target=scenario.can_hit_target,
                    estimated_completion_months=scenario.estimated_completion_months,
                    uses_credit=scenario.uses_credit,
                    primary_instrument=primary_instrument,
                    summary=summary,
                    color=config.color,
                    achievement=achievement,
                )
            )

        preferred_order = {"balanced": 2, "prudent": 1, "fast": 0}
        recommended = max(
            variants,
            key=lambda item: (
                item.achievement.score,
                1 if item.can_hit_target else 0,
                preferred_order[item.variant_id],
            ),
        )
        for item in variants:
            item.is_recommended = item.variant_id == recommended.variant_id

        return variants, recommended.variant_id

    async def build_goal_plan(
        self,
        user_id: int,
        data: GoalPlanRequest,
        locale: str = "ro",
    ) -> GoalPlanResponse:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Complete your financial profile first to receive a personalized plan."
                    if locale == "en"
                    else "Completeaza mai intai profilul financiar pentru a primi un plan personalizat."
                ),
            )

        requested_target_amount = data.target_amount
        requested_target_currency = data.target_currency.upper()
        reference_fx_rate = None
        normalized_target_amount = requested_target_amount
        if requested_target_currency == "EUR":
            reference_fx_rate = await self.market_offer_service.get_fx_rate("EUR")
            normalized_target_amount = round(requested_target_amount * reference_fx_rate, 2)

        monthly_capacity = self.risk_service.get_monthly_savings_capacity(profile)
        emergency_status = self.risk_service.get_emergency_fund_status(profile)
        simulator_max = self._build_simulator_max(profile.monthly_income, monthly_capacity)
        extra_monthly_savings = min(max(data.extra_monthly_savings, 0.0), simulator_max)
        effective_monthly_contribution = monthly_capacity + extra_monthly_savings
        emergency_target_months = emergency_status["target_months"]
        emergency_fund_target = emergency_status["target_amount"]
        emergency_months_current = (
            profile.emergency_fund / profile.monthly_expenses if profile.monthly_expenses else 0.0
        )
        debt_ratio = profile.debts / max(profile.monthly_income * 12, 1.0)

        base_scenario = self._compute_scenario(
            monthly_expenses=profile.monthly_expenses,
            goal_savings=profile.savings,
            emergency_fund=profile.emergency_fund,
            target_amount=normalized_target_amount,
            target_months=data.target_months,
            monthly_contribution=effective_monthly_contribution,
            emergency_months_kept=emergency_target_months,
            allows_credit=False,
            has_loan_options=False,
        )

        safe_saving_offers = await self.market_offer_service.get_safe_saving_offers(data.target_months)
        investment_options = await self.market_offer_service.get_investment_options(
            data.target_months,
            profile.risk_profile,
        )
        broker_options = await self.market_offer_service.get_broker_offers(
            target_months=data.target_months,
            has_market_instruments=bool(investment_options),
        )
        loan_options = []
        loan_product_family = None
        loan_market_scope: list[str] = []
        if data.allow_credit_gap and base_scenario.funding_gap > 0:
            loan_product_family = self.market_offer_service.determine_loan_offer_type(
                data.goal_name,
                base_scenario.funding_gap,
                data.target_months,
            )
            loan_market_scope = self.market_offer_service.get_top_bank_scope(loan_product_family)
            loan_options = await self.market_offer_service.get_loan_offers(
                base_scenario.funding_gap,
                data.target_months,
                data.goal_name,
            )

        base_scenario = self._compute_scenario(
            monthly_expenses=profile.monthly_expenses,
            goal_savings=profile.savings,
            emergency_fund=profile.emergency_fund,
            target_amount=normalized_target_amount,
            target_months=data.target_months,
            monthly_contribution=effective_monthly_contribution,
            emergency_months_kept=emergency_target_months,
            allows_credit=data.allow_credit_gap,
            has_loan_options=bool(loan_options),
        )

        achievement = self._build_achievement(
            target_amount=normalized_target_amount,
            target_months=data.target_months,
            scenario=base_scenario,
            emergency_months_current=emergency_months_current,
            debt_ratio=debt_ratio,
            locale=locale,
        )

        objective_pie = self._build_objective_pie(
            goal_name=data.goal_name,
            target_amount=normalized_target_amount,
            emergency_target=emergency_fund_target,
            debts=profile.debts,
            effective_monthly_contribution=effective_monthly_contribution,
            target_months=data.target_months,
            goals=profile.financial_goals or [],
            locale=locale,
        )

        plan_variants, recommended_variant_id = self._build_plan_variants(
            monthly_income=profile.monthly_income,
            monthly_expenses=profile.monthly_expenses,
            emergency_fund=profile.emergency_fund,
            savings=profile.savings,
            debts=profile.debts,
            target_months=data.target_months,
            target_amount=normalized_target_amount,
            effective_monthly_contribution=effective_monthly_contribution,
            safe_saving_offers=safe_saving_offers,
            investment_options=investment_options,
            loan_options=loan_options,
            allow_credit_gap=data.allow_credit_gap,
            emergency_target_months=emergency_target_months,
            locale=locale,
        )

        strategy_summary = self._build_strategy_summary(
            data.goal_name,
            normalized_target_amount,
            data.target_months,
            effective_monthly_contribution,
            base_scenario.available_now,
            base_scenario.projected_total,
            base_scenario.funding_gap,
            base_scenario.feasible_without_credit,
            profile.risk_profile,
            loan_product_family,
            locale,
        )
        next_actions = self._build_next_actions(
            data.goal_name,
            data.target_months,
            effective_monthly_contribution,
            emergency_target_months,
            emergency_fund_target,
            base_scenario.funding_gap,
            base_scenario.feasible_without_credit,
            profile.risk_profile,
            loan_product_family,
            locale,
        )

        return GoalPlanResponse(
            goal_name=data.goal_name,
            target_amount=round(normalized_target_amount, 2),
            requested_target_amount=round(requested_target_amount, 2),
            requested_target_currency=requested_target_currency,
            reference_fx_rate=reference_fx_rate,
            target_months=data.target_months,
            monthly_savings_capacity=round(monthly_capacity, 2),
            effective_monthly_contribution=round(effective_monthly_contribution, 2),
            emergency_fund_to_keep=round(emergency_fund_target, 2),
            available_now_for_goal=round(base_scenario.available_now, 2),
            projected_savings_by_deadline=round(base_scenario.projected_total, 2),
            funding_gap=round(base_scenario.funding_gap, 2),
            feasible_without_credit=base_scenario.feasible_without_credit,
            strategy_summary=strategy_summary,
            next_actions=next_actions,
            achievement=achievement,
            objective_pie=objective_pie,
            plan_variants=plan_variants,
            recommended_variant_id=recommended_variant_id,
            simulator_extra_monthly_savings=round(extra_monthly_savings, 2),
            simulator_max_extra_monthly_savings=round(simulator_max, 2),
            simulator_step=100.0,
            loan_product_family=loan_product_family,
            loan_product_family_label=self._loan_family_label(loan_product_family, locale),
            loan_market_scope=loan_market_scope,
            safe_saving_offers=safe_saving_offers,
            investment_options=investment_options,
            broker_options=broker_options,
            loan_options=loan_options,
        )

    def extract_goal_request(self, message: str, locale: str = "ro") -> GoalPlanRequest | None:
        lowered = message.lower()
        goal_keywords = (
            "vacanta",
            "concediu",
            "nunta",
            "masina",
            "avans",
            "casa",
            "apartament",
            "locuinta",
            "ipoteca",
            "imobil",
            "telefon",
            "laptop",
            "urgenta",
            "fond",
            "obiectiv",
            "vacation",
            "holiday",
            "wedding",
            "car",
            "down payment",
            "house",
            "home",
            "apartment",
            "mortgage",
            "property",
            "phone",
            "emergency",
            "goal",
        )
        if not any(keyword in lowered for keyword in goal_keywords):
            return None

        amount_match = re.search(r"([\d\s.,]+)\s*(lei|ron|eur|euro)", lowered)
        if not amount_match:
            return None
        amount = self._parse_amount(amount_match.group(1))
        target_currency = "EUR" if amount_match.group(2) in {"eur", "euro"} else "RON"

        months_match = re.search(r"(\d+)\s*(luni?|months?)", lowered)
        years_match = re.search(r"(\d+)\s*(ani?|years?)", lowered)
        if months_match:
            target_months = int(months_match.group(1))
        elif years_match:
            target_months = int(years_match.group(1)) * 12
        else:
            target_months = 6

        goal_name = "financial goal" if is_english(locale) else "obiectiv financiar"
        phrase_match = re.search(
            r"(?:vreau|pentru|obiectiv(?:ul)?(?: de)?|i want|for|goal(?: of)?)\s+(?:un|o|a|an)?\s*([\w\s-]{3,40}?)\s+de\s+[\d\s.,]+\s*(?:lei|ron|eur|euro)",
            message,
            flags=re.IGNORECASE,
        )
        if phrase_match:
            goal_name = phrase_match.group(1).strip()
        else:
            for keyword in goal_keywords:
                if keyword in lowered:
                    goal_name = keyword
                    break

        allow_credit_gap = not any(
            phrase in lowered
            for phrase in ("fara credit", "nu vreau credit", "without credit", "no loan", "no credit")
        )
        return GoalPlanRequest(
            goal_name=goal_name,
            target_amount=amount,
            target_currency=target_currency,
            target_months=target_months,
            allow_credit_gap=allow_credit_gap,
        )

    def render_chat_goal_plan(self, plan: GoalPlanResponse, locale: str = "ro") -> str:
        english = is_english(locale)
        lines = (
            [
                f'For your goal "{plan.goal_name}" of {plan.target_amount:.0f} RON in {plan.target_months} months:',
                f"- you can save about {plan.effective_monthly_contribution:.0f} RON per month;",
                f"- without going below your safety buffer, you currently have about {plan.available_now_for_goal:.0f} RON available;",
                f"- by the deadline you could reach about {plan.projected_savings_by_deadline:.0f} RON in total;",
                f'- the current achievement score is about {plan.achievement.score}/100 ({plan.achievement.label.lower()}).',
            ]
            if english
            else [
                f'Pentru obiectivul tau "{plan.goal_name}" de {plan.target_amount:.0f} lei in {plan.target_months} luni:',
                f"- poti economisi aproximativ {plan.effective_monthly_contribution:.0f} lei pe luna;",
                f"- fara sa cobori sub fondul de siguranta, ai disponibil acum cam {plan.available_now_for_goal:.0f} lei;",
                f"- pana la termen poti strange in total aproximativ {plan.projected_savings_by_deadline:.0f} lei;",
                f"- scorul curent de realizare este de aproximativ {plan.achievement.score}/100 ({plan.achievement.label.lower()}).",
            ]
        )

        if plan.requested_target_currency == "EUR" and plan.reference_fx_rate:
            lines.append(
                f"- I converted the requested amount using the latest BNR EUR/RON rate of about {plan.reference_fx_rate:.4f}."
                if english
                else f"- Am convertit suma ceruta folosind ultimul curs oficial BNR EUR/RON de aproximativ {plan.reference_fx_rate:.4f}."
            )

        if plan.feasible_without_credit:
            lines.append(
                "The goal looks achievable without credit, so it would usually be healthier to rely on deposits, government bonds, or other prudent instruments matched to the timeline."
                if english
                else "Obiectivul pare realizabil fara credit, deci ar fi mai sanatos sa folosesti depozite, titluri de stat sau instrumente prudente potrivite termenului."
            )
        else:
            lines.append(
                f"You are still short about {plan.funding_gap:.0f} RON. If you want to keep the current deadline, you could combine saving with financing for the difference."
                if english
                else f"Iti mai lipsesc aproximativ {plan.funding_gap:.0f} lei. Daca vrei sa mergi totusi mai departe, poti combina economisirea cu un credit pentru diferenta."
            )

        if plan.loan_options:
            best_loan = plan.loan_options[0]
            lines.append(
                (
                    f'I checked the current public {plan.loan_product_family_label.lower()} offers across the top {len(plan.loan_market_scope)} major Romanian banks relevant for this case and found {len(plan.loan_options)} comparable offers.'
                    if english and plan.loan_product_family_label
                    else f'Am verificat ofertele publice curente de tip {plan.loan_product_family_label.lower()} in top {len(plan.loan_market_scope)} banci mari din Romania relevante pentru acest caz si am gasit {len(plan.loan_options)} oferte comparabile.'
                )
            )
            if best_loan.dae_percent is not None and best_loan.indicative_monthly_payment is not None:
                lines.append(
                    (
                        f"The strongest public option right now looks like {best_loan.product_name} from {best_loan.provider}, with APR around {best_loan.dae_percent:.2f}% and an estimated payment of {best_loan.indicative_monthly_payment:.0f} RON/month."
                        if english
                        else f"Cea mai buna optiune publica acum pare {best_loan.product_name} de la {best_loan.provider}, cu DAE de aproximativ {best_loan.dae_percent:.2f}% si o rata estimata de {best_loan.indicative_monthly_payment:.0f} lei/luna."
                    )
                )

        best_safe = plan.safe_saving_offers[0] if plan.safe_saving_offers else None
        if best_safe and best_safe.annual_rate_percent is not None:
            lines.append(
                f"The best prudent option found right now is {best_safe.product_name} from {best_safe.provider}, at about {best_safe.annual_rate_percent:.2f}% per year."
                if english
                else f"Cea mai buna varianta prudenta gasita acum este {best_safe.product_name} de la {best_safe.provider}, cu aproximativ {best_safe.annual_rate_percent:.2f}% pe an."
            )

        if plan.broker_options:
            top_brokers = ", ".join(offer.provider for offer in plan.broker_options[:3])
            lines.append(
                f"For execution, I also compared brokers relevant for Romanian investors. The most useful low-cost names in the current list are {top_brokers}."
                if english
                else f"Pentru executie, am comparat si brokeri relevanti pentru investitorii din Romania. In lista curenta, numele cele mai utile ca raport cost-acces sunt {top_brokers}."
            )

        best_variant = next(
            (variant for variant in plan.plan_variants if variant.variant_id == plan.recommended_variant_id),
            None,
        )
        if best_variant:
            lines.append(
                f'The strongest route right now looks like the "{best_variant.title}" variant.'
                if english
                else f'Cea mai puternica directie acum pare varianta "{best_variant.title}".'
            )

        return "\n".join(lines)

    def _build_strategy_summary(
        self,
        goal_name: str,
        target_amount: float,
        target_months: int,
        monthly_capacity: float,
        available_now: float,
        projected: float,
        funding_gap: float,
        feasible_without_credit: bool,
        risk_profile: str,
        loan_product_family: str | None,
        locale: str = "ro",
    ) -> str:
        english = is_english(locale)
        if target_months <= 12:
            base = (
                f"The goal {goal_name} is short-term, so capital protection should matter more than aggressive returns."
                if english
                else f"Obiectivul {goal_name} este unul de termen scurt, asa ca prioritatea ar trebui sa fie protectia capitalului, nu randamentele agresive."
            )
        elif target_months <= 36:
            base = (
                f"The goal {goal_name} has a medium horizon, which allows a mix of safe saving and moderate instruments depending on your {risk_profile} risk profile."
                if english
                else f"Obiectivul {goal_name} are un orizont mediu, ceea ce permite combinarea economisirii sigure cu instrumente moderate, in functie de profilul tau de risc {risk_profile}."
            )
        else:
            base = (
                f"The goal {goal_name} has a long enough horizon to consider ETFs or other growth instruments alongside classic saving."
                if english
                else f"Obiectivul {goal_name} are un orizont suficient de lung pentru a lua in calcul si fonduri ETF sau alte instrumente de crestere, pe langa economisirea clasica."
            )

        if feasible_without_credit:
            ending = (
                f"With a monthly effort of about {monthly_capacity:.0f} RON and {available_now:.0f} RON available now, you could reach around {projected:.0f} RON by the deadline, so the {target_amount:.0f} RON target looks feasible without credit."
                if english
                else f"Cu un efort lunar de aproximativ {monthly_capacity:.0f} lei si {available_now:.0f} lei disponibili acum, poti ajunge la aproximativ {projected:.0f} lei pana la termen, deci obiectivul de {target_amount:.0f} lei pare fezabil fara credit."
            )
        else:
            ending = (
                (
                    f"At your current pace you could reach around {projected:.0f} RON, leaving a gap of {funding_gap:.0f} RON. That means the strategy is either to extend the timeline, increase saving, or cover the difference with a mortgage."
                    if loan_product_family == "mortgage"
                    else (
                        f"At your current pace you could reach around {projected:.0f} RON, leaving a gap of {funding_gap:.0f} RON. That means the strategy is either to extend the timeline, increase saving, or cover the difference with a secured personal loan."
                        if loan_product_family == "secured_personal_loan"
                        else f"At your current pace you could reach around {projected:.0f} RON, leaving a gap of {funding_gap:.0f} RON. That means the strategy is either to extend the timeline, increase saving, or finance the difference externally."
                    )
                )
                if english
                else (
                    f"Cu ritmul tau actual poti ajunge la aproximativ {projected:.0f} lei, ceea ce lasa un deficit de {funding_gap:.0f} lei. De aceea, strategia poate fi fie amanarea termenului, fie cresterea economisirii, fie acoperirea diferentei prin credit ipotecar/imobiliar."
                    if loan_product_family == "mortgage"
                    else (
                        f"Cu ritmul tau actual poti ajunge la aproximativ {projected:.0f} lei, ceea ce lasa un deficit de {funding_gap:.0f} lei. De aceea, strategia poate fi fie amanarea termenului, fie cresterea economisirii, fie acoperirea diferentei prin credit de nevoi personale cu ipoteca."
                        if loan_product_family == "secured_personal_loan"
                        else f"Cu ritmul tau actual poti ajunge la aproximativ {projected:.0f} lei, ceea ce lasa un deficit de {funding_gap:.0f} lei. De aceea, strategia poate fi fie amanarea termenului, fie cresterea economisirii, fie acoperirea diferentei prin finantare externa."
                    )
                )
            )
        return f"{base} {ending}"

    def _build_next_actions(
        self,
        goal_name: str,
        target_months: int,
        monthly_capacity: float,
        emergency_target_months: int,
        emergency_fund_target: float,
        funding_gap: float,
        feasible_without_credit: bool,
        risk_profile: str,
        loan_product_family: str | None,
        locale: str = "ro",
    ) -> list[str]:
        english = is_english(locale)
        actions = [
            (
                f"Set an automatic monthly contribution of about {monthly_capacity:.0f} RON for this goal."
                if english
                else f"Seteaza automat o economisire lunara de aproximativ {monthly_capacity:.0f} lei pentru acest obiectiv."
            ),
            (
                f"Keep around {emergency_fund_target:.0f} RON separately, meaning about {emergency_target_months} months of expenses, before using savings for {goal_name}."
                if english
                else f"Mentine separat aproximativ {emergency_fund_target:.0f} lei, adica in jur de {emergency_target_months} luni de cheltuieli, ca fond minim de urgenta inainte sa folosesti economiile pentru {goal_name}."
            ),
            (
                "Move the simulator slider until the score enters the green zone and compare the three plan variants before choosing one."
                if english
                else "Muta sliderul din simulator pana cand scorul intra in zona verde si compara cele trei variante de plan inainte sa alegi una."
            ),
        ]

        if target_months <= 12:
            actions.append(
                "For a short timeline, prioritize deposits and government securities instead of volatile stocks."
                if english
                else "Pentru termen scurt, prioritizeaza depozite si titluri de stat in locul actiunilor volatile."
            )
        elif target_months <= 36:
            actions.append(
                "For a medium timeline, you can combine deposits or government securities with a prudent bond fund or ETF."
                if english
                else "Pentru termen mediu, poti combina depozite sau titluri de stat cu un fond de obligatiuni sau ETF prudent."
            )
        elif risk_profile == "aggressive":
            actions.append(
                "For a long timeline and aggressive profile, the base can be a global ETF with a small sleeve of individual stocks."
                if english
                else "Pentru termen lung si profil agresiv, baza poate fi un ETF global, cu o componenta mica in actiuni individuale."
            )
        else:
            actions.append(
                "For a longer timeline, you can combine safe instruments with diversified funds or ETFs."
                if english
                else "Pentru termen mai lung, poti combina instrumente sigure cu fonduri sau ETF-uri diversificate."
            )

        if not feasible_without_credit and funding_gap > 0:
            actions.append(
                (
                    f"If you want to keep the current deadline, compare mortgage offers for the remaining amount of about {funding_gap:.0f} RON instead of forcing a personal loan."
                    if loan_product_family == "mortgage"
                    else (
                        f"If you want to keep the current deadline, compare secured personal loans with property collateral for the remaining amount of about {funding_gap:.0f} RON."
                        if loan_product_family == "secured_personal_loan"
                        else f"If you want to keep the current deadline, compare financing only for the remaining gap of about {funding_gap:.0f} RON."
                    )
                )
                if english
                else (
                    f"Daca vrei sa mentii termenul actual, compara credite ipotecare/imobiliare pentru suma ramasa de aproximativ {funding_gap:.0f} lei, nu forta un credit de nevoi personale."
                    if loan_product_family == "mortgage"
                    else (
                        f"Daca vrei sa mentii termenul actual, compara credite de nevoi personale cu ipoteca pentru suma ramasa de aproximativ {funding_gap:.0f} lei."
                        if loan_product_family == "secured_personal_loan"
                        else f"Daca vrei sa mentii termenul actual, compara un credit doar pentru diferenta de aproximativ {funding_gap:.0f} lei."
                    )
                )
            )
        return actions
