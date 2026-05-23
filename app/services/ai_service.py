import httpx

from app.config import settings
from app.utils.locale import is_english


class AIService:
    """
    Groq AI wrapper with a rule-based fallback for local development.
    """

    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def is_groq_configured(self) -> bool:
        api_key = settings.groq_api_key.strip()
        invalid_markers = ("replace", "your_", "test_key")
        return bool(api_key) and not any(marker in api_key.lower() for marker in invalid_markers)

    async def _call_groq(self, system_prompt: str, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.GROQ_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _build_recommendation_fallback(
        self,
        profile_data: dict,
        allocation: dict,
        risk_score: int,
        health_score: int,
        locale: str = "ro",
    ) -> str:
        income = profile_data.get("monthly_income", 0.0)
        expenses = profile_data.get("monthly_expenses", 0.0)
        emergency_fund = profile_data.get("emergency_fund", 0.0)
        emergency_target_months = profile_data.get("emergency_fund_target_months", 6)
        savings = profile_data.get("savings", 0.0)
        debts = profile_data.get("debts", 0.0)
        monthly_debt_obligations = profile_data.get("monthly_debt_obligations", 0.0)
        goals = profile_data.get("financial_goals", [])
        surplus = income - expenses - monthly_debt_obligations
        emergency_months = emergency_fund / expenses if expenses else 0.0
        english = is_english(locale)

        strengths: list[str] = []
        improvements: list[str] = []

        if surplus > 0:
            strengths.append(
                (
                    f"you have an estimated monthly surplus of {surplus:.0f} RON, which supports steady investing"
                    if english
                    else f"ai un surplus lunar estimat de {surplus:.0f} RON, ceea ce iti permite sa investesti constant"
                )
            )
        else:
            improvements.append(
                (
                    "your expenses are too close to your income, so budget optimization should come first"
                    if english
                    else "cheltuielile sunt prea aproape de venit si merita sa prioritizezi optimizarea bugetului"
                )
            )

        if emergency_months >= emergency_target_months:
            strengths.append(
                (
                    f"you already have an emergency fund covering about {emergency_months:.1f} months of living expenses"
                    if english
                    else f"ai deja un fond de urgenta de aproximativ {emergency_months:.1f} luni de cheltuieli de baza"
                )
            )
        else:
            improvements.append(
                (
                    f"your emergency fund covers only {emergency_months:.1f} months and should move closer to {emergency_target_months} months"
                    if english
                    else f"fondul de urgenta acopera doar {emergency_months:.1f} luni si ar trebui apropiat de tinta de {emergency_target_months} luni"
                )
            )

        if debts > income * 6:
            improvements.append(
                "your debt level is high and should stay under control"
                if english
                else "nivelul datoriilor este ridicat si trebuie tinut sub control"
            )
        elif debts == 0:
            strengths.append(
                "you have no debt, which gives you more flexibility"
                if english
                else "nu ai datorii, ceea ce iti ofera mai multa flexibilitate"
            )
        if monthly_debt_obligations > 0:
            improvements.append(
                (
                    f"you already have monthly loan obligations of about {monthly_debt_obligations:.0f} RON, which reduces the room available for new goals"
                    if english
                    else f"ai deja obligatii lunare de credit de aproximativ {monthly_debt_obligations:.0f} RON, ceea ce reduce spatiul disponibil pentru obiective noi"
                )
            )

        goal_text = ", ".join(goals) if goals else (
            "long-term financial stability" if english else "stabilitate financiara pe termen lung"
        )
        strengths_text = "; ".join(strengths) if strengths else (
            "your profile already has a few healthy foundations"
            if english
            else "profilul tau are cateva baze bune"
        )
        improvements_text = "; ".join(improvements) if improvements else (
            "you can continue with monthly discipline and diversified investing"
            if english
            else "poti continua cu disciplina lunara si investitii diversificate"
        )

        if english:
            return (
                f"Your risk score is {risk_score}/100 and your financial health score is {health_score}/100. "
                f"For goals such as {goal_text}, the suggested allocation focuses on diversification and risk control.\n\n"
                f"The proposed structure is {allocation.get('etf_global', 0)}% global ETF, "
                f"{allocation.get('bonds', 0)}% bonds, {allocation.get('cash', 0)}% cash or emergency fund, "
                f"and {allocation.get('high_risk', 0)}% higher-risk assets. This mix aims to preserve enough liquidity "
                f"while still giving you growth exposure without pushing risk beyond what your current situation supports.\n\n"
                f"You currently keep about {savings:.0f} RON separately for goals or investments and {emergency_fund:.0f} RON in the emergency fund. "
                f"Strengths: {strengths_text}. Areas to improve: {improvements_text}. "
                f"The next useful step is to invest monthly after keeping your budget stable and your emergency fund healthy."
            )

        return (
            f"Scorul tau de risc este {risk_score}/100, iar scorul de sanatate financiara este "
            f"{health_score}/100. Pentru obiective precum {goal_text}, alocarea propusa pune accent pe "
            f"diversificare si controlul riscului.\n\n"
            f"Structura recomandata este {allocation.get('etf_global', 0)}% ETF global, "
            f"{allocation.get('bonds', 0)}% obligatiuni, {allocation.get('cash', 0)}% cash sau fond de urgenta "
            f"si {allocation.get('high_risk', 0)}% active cu risc ridicat. Aceasta combinatie urmareste sa "
            f"pastreze lichiditatea necesara si sa iti ofere expunere la crestere fara sa forteze un nivel de risc "
            f"mai mare decat poate sustine situatia actuala.\n\n"
            f"Ai separat aproximativ {savings:.0f} RON pentru obiective sau investitii si {emergency_fund:.0f} RON in fondul de urgenta. "
            f"Puncte forte: {strengths_text}. Zone de imbunatatit: {improvements_text}. "
            f"Pasul urmator recomandat este sa investesti lunar dupa ce mentii un buget stabil si un fond de urgenta sanatos."
        )

    def _build_financial_summary_fallback(self, profile_data: dict, locale: str = "ro") -> str:
        income = profile_data.get("monthly_income", 0.0)
        expenses = profile_data.get("monthly_expenses", 0.0)
        emergency_fund = profile_data.get("emergency_fund", 0.0)
        emergency_target_months = profile_data.get("emergency_fund_target_months", 6)
        savings = profile_data.get("savings", 0.0)
        debts = profile_data.get("debts", 0.0)
        monthly_debt_obligations = profile_data.get("monthly_debt_obligations", 0.0)
        surplus = income - expenses - monthly_debt_obligations
        emergency_months = emergency_fund / expenses if expenses else 0.0
        english = is_english(locale)

        if surplus > 0:
            base = (
                f"You have an estimated monthly surplus of {surplus:.0f} RON."
                if english
                else f"Ai un surplus lunar estimat de {surplus:.0f} RON."
            )
        else:
            base = (
                "Your expenses are consuming almost all of your monthly income."
                if english
                else "Cheltuielile iti consuma aproape tot venitul lunar."
            )

        if emergency_months >= emergency_target_months:
            safety = (
                f"Your emergency fund covers about {emergency_months:.1f} months, against a target of {emergency_target_months} months."
                if english
                else f"Fondul de urgenta acopera aproximativ {emergency_months:.1f} luni, fata de o tinta de {emergency_target_months} luni."
            )
        else:
            safety = (
                f"Your emergency fund is still small, at about {emergency_months:.1f} months versus a target of {emergency_target_months}."
                if english
                else f"Fondul de urgenta este inca mic, la aproximativ {emergency_months:.1f} luni fata de tinta de {emergency_target_months}."
            )

        debt_note = (
            "Debt is low relative to your income."
            if debts <= income * 3 and english
            else "Datoriile sunt reduse raportat la venit."
            if debts <= income * 3
            else "Debt deserves attention before increasing investments."
            if english
            else "Datoriile merita atentia ta inainte de cresterea investitiilor."
        )
        if monthly_debt_obligations > 0:
            debt_note += (
                f" Existing monthly loan obligations are about {monthly_debt_obligations:.0f} RON."
                if english
                else f" Obligatiile lunare existente din credite sunt de aproximativ {monthly_debt_obligations:.0f} RON."
            )

        savings_note = (
            f"You keep about {savings:.0f} RON separately for goals or investing."
            if english
            else f"Pastrezi separat aproximativ {savings:.0f} RON pentru obiective sau investitii."
        )
        return f"{base} {safety} {savings_note} {debt_note}"

    def _build_chat_fallback(self, message: str, context: dict, locale: str = "ro") -> str:
        lowered = message.lower()
        has_profile = context.get("has_profile", False)
        has_recommendation = context.get("has_recommendation", False)
        english = is_english(locale)

        if not has_profile:
            return (
                "I can answer in general terms, but for a personal answer please complete your financial profile first. "
                "Start with income, expenses, savings, debts, existing monthly loan obligations, and your main goals."
                if english
                else "Pot sa iti raspund generic, dar pentru un raspuns personalizat completeaza mai intai profilul "
                "financiar. Incepe cu venit, cheltuieli, economii, datorii, obligatii lunare existente si obiectivele tale principale."
            )

        savings_capacity = context.get("monthly_savings_capacity", 0.0)
        emergency_months = context.get("emergency_fund_months", 0.0)
        emergency_target_months = context.get("emergency_fund_target_months", 6)
        emergency_fund_amount = context.get("emergency_fund_amount", 0.0)
        monthly_debt_obligations = context.get("monthly_debt_obligations", 0.0)
        risk_score = context.get("risk_score")
        health_score = context.get("financial_health_score")
        allocation = context.get("recommendation_allocation", {})
        goals = context.get("financial_goals", [])
        goal_text = ", ".join(goals) if goals else ("your current goals" if english else "obiectivele tale actuale")

        if "urgenta" in lowered or "emergency" in lowered:
            return (
                f"Based on your current profile, your emergency fund covers about {emergency_months:.1f} months of expenses. "
                f"Your current target is {emergency_target_months} months, so until you get there, prioritize cash or very liquid accounts before increasing volatile investments."
                if english
                else f"Pe profilul tau actual, fondul de urgenta acopera aproximativ {emergency_months:.1f} luni de cheltuieli. "
                f"Tinta ta actuala este de {emergency_target_months} luni, iar pana ajungi acolo pune prioritate pe cash sau conturi foarte lichide "
                "inainte sa cresti partea de investitii volatile."
            )

        if any(keyword in lowered for keyword in ("invest", "etf", "portof", "aloc", "portfolio", "allocation")):
            if has_recommendation:
                return (
                    f"Your latest suggested allocation is {allocation.get('etf_global', 0)}% global ETF, "
                    f"{allocation.get('bonds', 0)}% bonds, {allocation.get('cash', 0)}% cash, and "
                    f"{allocation.get('high_risk', 0)}% higher-risk assets. It fits a risk score of {risk_score}/100 "
                    "and should be implemented gradually through steady monthly contributions."
                    if english
                    else f"Ultima alocare recomandata pentru tine este {allocation.get('etf_global', 0)}% ETF global, "
                    f"{allocation.get('bonds', 0)}% obligatiuni, {allocation.get('cash', 0)}% cash si "
                    f"{allocation.get('high_risk', 0)}% active cu risc ridicat. Ea se potriveste unui scor de risc "
                    f"de {risk_score}/100 si ar trebui implementata treptat, prin contributii lunare constante."
                )
            return (
                f"Your monthly savings capacity is about {savings_capacity:.0f} RON. Generate a recommendation first "
                "from the planning section to see which allocation fits your profile."
                if english
                else f"Capacitatea ta lunara de economisire este de aproximativ {savings_capacity:.0f} RON. "
                "Genereaza mai intai o recomandare din sectiunea de plan pentru a vedea ce alocare se potriveste "
                "profilului tau."
            )

        if any(keyword in lowered for keyword in ("dator", "credit", "imprumut", "loan", "debt")):
            return (
                f"Your financial health score is {health_score}/100. If you have high-interest loans, it is usually worth "
                f"reducing those in parallel with building an emergency fund. You already have about {monthly_debt_obligations:.0f} RON/month in loan obligations, so aggressive investing should stay secondary."
                if english
                else f"Scorul tau de sanatate financiara este {health_score}/100. Daca ai credite cu dobanzi mari, "
                f"merita sa reduci acele datorii in paralel cu construirea unui fond de urgenta. Ai deja aproximativ {monthly_debt_obligations:.0f} RON/luna in obligatii de credit, iar investitiile "
                "agresive sa ramana pe planul doi."
            )

        if has_recommendation:
            return (
                f"Based on your profile, you have a risk score of {risk_score}/100, a financial health score of "
                f"{health_score}/100, and a monthly savings capacity of about {savings_capacity:.0f} RON. "
                f"For {goal_text}, the next useful step is to follow the allocation already generated and review progress monthly."
                if english
                else f"Pe baza profilului tau, ai un scor de risc de {risk_score}/100, un scor de sanatate financiara "
                f"de {health_score}/100 si o capacitate lunara de economisire de aproximativ {savings_capacity:.0f} RON. "
                f"Pentru {goal_text}, urmatorul pas util este sa urmezi alocarea deja generata si sa revizuiesti lunar "
                "progresul."
            )

        return (
            f"Based on your current profile, your monthly savings capacity is about {savings_capacity:.0f} RON, your existing monthly loan obligations are about {monthly_debt_obligations:.0f} RON, and your "
            f"emergency fund covers {emergency_months:.1f} months ({emergency_fund_amount:.0f} RON) against a target of {emergency_target_months} months. Complete the recommendation step to turn this into a concrete plan."
            if english
            else f"Pe baza profilului tau actual, ai o capacitate lunara de economisire de aproximativ "
            f"{savings_capacity:.0f} RON, ai deja aproximativ {monthly_debt_obligations:.0f} RON/luna in obligatii de credit si un fond de urgenta de {emergency_months:.1f} luni ({emergency_fund_amount:.0f} RON) fata de o tinta de {emergency_target_months} luni. "
            "Completeaza pasul de recomandare pentru a transforma aceste date intr-un plan concret de alocare."
        )

    async def generate_recommendations(
        self,
        profile_data: dict,
        allocation: dict,
        risk_score: int,
        health_score: int,
        locale: str = "ro",
    ) -> str:
        english = is_english(locale)
        system_prompt = (
            "You are a friendly educational financial coach. "
            "Explain financial decisions clearly and simply. "
            "Do not promise returns. Use an encouraging, practical tone. Respond in English."
            if english
            else "Esti un consilier financiar educativ si prietenos. "
            "Explici simplu si clar deciziile financiare. "
            "Nu oferi garantii de randament. "
            "Folosesti un ton incurajator si practic. "
            "Raspunzi in limba romana."
        )
        user_message = (
            f"""
Financial profile:
- Monthly income: {profile_data.get('monthly_income')} RON
- Monthly expenses: {profile_data.get('monthly_expenses')} RON
- Existing monthly loan obligations: {profile_data.get('monthly_debt_obligations')} RON
- Emergency fund: {profile_data.get('emergency_fund')} RON
- Goal / investment savings: {profile_data.get('savings')} RON
- Debts: {profile_data.get('debts')} RON
- Risk profile: {profile_data.get('risk_profile')}
- Goals: {', '.join(profile_data.get('financial_goals', []))}
- Emergency fund target: {profile_data.get('emergency_fund_target_months', 6)} months

Calculated risk score: {risk_score}/100
Financial health score: {health_score}/100

Suggested allocation:
- Global ETF: {allocation.get('etf_global')}%
- Bonds: {allocation.get('bonds')}%
- Cash / emergency fund: {allocation.get('cash')}%
- High-risk assets: {allocation.get('high_risk')}%

Explain in 3-4 paragraphs why this allocation fits.
Mention strengths and what could be improved.
"""
            if english
            else f"""
Profil financiar al utilizatorului:
- Venit lunar: {profile_data.get('monthly_income')} RON
- Cheltuieli lunare: {profile_data.get('monthly_expenses')} RON
- Obligatii lunare existente din credite: {profile_data.get('monthly_debt_obligations')} RON
- Fond de urgenta: {profile_data.get('emergency_fund')} RON
- Economii pentru obiective / investitii: {profile_data.get('savings')} RON
- Datorii: {profile_data.get('debts')} RON
- Profil risc: {profile_data.get('risk_profile')}
- Obiective: {', '.join(profile_data.get('financial_goals', []))}
- Tinta fond urgenta: {profile_data.get('emergency_fund_target_months', 6)} luni

Scor risc calculat: {risk_score}/100
Scor sanatate financiara: {health_score}/100

Alocare recomandata:
- ETF Global: {allocation.get('etf_global')}%
- Obligatiuni: {allocation.get('bonds')}%
- Cash/Fond urgenta: {allocation.get('cash')}%
- Active cu risc ridicat: {allocation.get('high_risk')}%

Explica in 3-4 paragrafe de ce aceasta alocare este potrivita.
Mentioneaza punctele forte si ce ar putea imbunatati.
"""
        )
        if not self.is_groq_configured():
            return self._build_recommendation_fallback(
                profile_data, allocation, risk_score, health_score, locale
            )

        try:
            return await self._call_groq(system_prompt, user_message)
        except httpx.HTTPError:
            return self._build_recommendation_fallback(
                profile_data, allocation, risk_score, health_score, locale
            )

    async def generate_financial_summary(self, profile_data: dict, locale: str = "ro") -> str:
        english = is_english(locale)
        system_prompt = (
            "You are a concise financial analyst. Give a clear summary in English, in at most 3 sentences."
            if english
            else "Esti un analist financiar succint. "
            "Oferi un rezumat clar al situatiei financiare. "
            "Raspunzi in romana, in maximum 3 fraze."
        )
        user_message = (
            f"""
Analyze this financial situation and give a short summary:
Income: {profile_data.get('monthly_income')} RON/month
Expenses: {profile_data.get('monthly_expenses')} RON/month
Existing monthly loan obligations: {profile_data.get('monthly_debt_obligations')} RON/month
Emergency fund: {profile_data.get('emergency_fund')} RON
Goal / investment savings: {profile_data.get('savings')} RON
Debts: {profile_data.get('debts')} RON
"""
            if english
            else f"""
Analizeaza aceasta situatie financiara si ofera un rezumat:
Venit: {profile_data.get('monthly_income')} RON/luna
Cheltuieli: {profile_data.get('monthly_expenses')} RON/luna
Obligatii lunare existente din credite: {profile_data.get('monthly_debt_obligations')} RON/luna
Fond de urgenta: {profile_data.get('emergency_fund')} RON
Economii pentru obiective / investitii: {profile_data.get('savings')} RON
Datorii: {profile_data.get('debts')} RON
"""
        )
        if not self.is_groq_configured():
            return self._build_financial_summary_fallback(profile_data, locale)

        try:
            return await self._call_groq(system_prompt, user_message)
        except httpx.HTTPError:
            return self._build_financial_summary_fallback(profile_data, locale)

    async def chat_response(self, message: str, context: dict, locale: str = "ro") -> str:
        english = is_english(locale)
        system_prompt = (
            f"""
You are an educational financial assistant. You help users understand personal finance.

User context:
- Monthly income: {context.get('monthly_income', 'unknown')} RON
- Expenses: {context.get('monthly_expenses', 'unknown')} RON
- Existing monthly loan obligations: {context.get('monthly_debt_obligations', 'unknown')} RON
- Emergency fund: {context.get('emergency_fund_amount', 'unknown')} RON
- Emergency fund target: {context.get('emergency_fund_target_months', 'unknown')} months
- Goal / investment savings: {context.get('savings', 'unknown')} RON
- Risk profile: {context.get('risk_profile', 'moderate')}
- Goals: {', '.join(context.get('financial_goals', []))}
- Risk score: {context.get('risk_score', 'unknown')}
- Financial health score: {context.get('financial_health_score', 'unknown')}
- Current allocation: {context.get('recommendation_allocation', {})}

Important rules:
1. Respond simply and educationally in English.
2. Do not provide guaranteed financial advice.
3. Do not recommend products with guaranteed returns.
4. Encourage diversification and discipline.
5. If unsure, suggest consulting a specialist.
"""
            if english
            else f"""
Esti un asistent financiar educativ. Ajuti utilizatorii sa inteleaga finantele personale.

Context utilizator:
- Venit lunar: {context.get('monthly_income', 'necunoscut')} RON
- Cheltuieli: {context.get('monthly_expenses', 'necunoscut')} RON
- Obligatii lunare existente din credite: {context.get('monthly_debt_obligations', 'necunoscut')} RON
- Fond de urgenta: {context.get('emergency_fund_amount', 'necunoscut')} RON
- Tinta fond urgenta: {context.get('emergency_fund_target_months', 'necunoscut')} luni
- Economii pentru obiective / investitii: {context.get('savings', 'necunoscut')} RON
- Profil risc: {context.get('risk_profile', 'moderat')}
- Obiective: {', '.join(context.get('financial_goals', []))}
- Scor risc: {context.get('risk_score', 'necunoscut')}
- Scor sanatate financiara: {context.get('financial_health_score', 'necunoscut')}
- Alocare curenta: {context.get('recommendation_allocation', {})}

Reguli importante:
1. Raspunde simplu si educativ in romana.
2. Nu oferi sfaturi financiare garantate.
3. Nu recomanda produse financiare specifice cu garantii.
4. Incurajeaza diversificarea si disciplina financiara.
5. Daca nu stii, recomanda consultarea unui specialist.
"""
        )
        if not self.is_groq_configured():
            return self._build_chat_fallback(message, context, locale)

        try:
            return await self._call_groq(system_prompt, message)
        except httpx.HTTPError:
            return self._build_chat_fallback(message, context, locale)
