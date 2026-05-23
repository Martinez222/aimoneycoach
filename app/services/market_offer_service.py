import asyncio
import math
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
from io import BytesIO

import httpx
from pypdf import PdfReader

from app.schemas.goal_schema import MarketOfferResponse


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
)

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

TOP_10_BANKS = [
    "Banca Transilvania",
    "BCR",
    "CEC Bank",
    "UniCredit Bank",
    "BRD",
    "Raiffeisen Bank",
    "ING",
    "Exim Banca Romaneasca",
    "Garanti BBVA",
    "Libra Internet Bank",
]

PERSONAL_UNSECURED_BANK_SCOPE = TOP_10_BANKS
SECURED_PERSONAL_BANK_SCOPE = [
    "CEC Bank",
    "Garanti BBVA",
    "Libra Internet Bank",
]
MORTGAGE_BANK_SCOPE = [
    "Banca Transilvania",
    "BCR",
    "CEC Bank",
    "UniCredit Bank",
    "BRD",
    "Raiffeisen Bank",
    "ING",
    "Exim Banca Romaneasca",
    "Garanti BBVA",
]

BANK_RANKS = {bank_name: index + 1 for index, bank_name in enumerate(TOP_10_BANKS)}
UNSECURED_PERSONAL_MARKET_LIMIT_RON = 150000.0
CREDIT_MATURITY_AGE_BY_GENDER = {
    "male": 70,
    "female": 65,
}
MORTGAGE_MATURITY_AGE = 70
PRODUCT_MAX_TERM_MONTHS = {
    "personal_unsecured_loan": 60,
    "secured_personal_loan": 120,
    "mortgage": 360,
}
MIN_LOAN_TERM_MONTHS = 12


@dataclass(frozen=True)
class QuoteInstrument:
    symbol: str
    name: str
    category: str
    suitability: str
    currency: str
    source_url: str
    source_name: str
    note: str
    term_months: int | None = None
    annual_cost_percent: float | None = None
    transaction_cost_percent: float | None = None
    subscription_fee_percent: float | None = None
    redemption_fee_percent: float | None = None
    custody_fee_percent: float | None = None
    cost_summary: str | None = None


class MarketOfferService:
    _text_cache: dict[str, tuple[float, str]] = {}
    _pdf_cache: dict[str, tuple[float, str]] = {}
    _fx_cache: dict[str, tuple[float, float]] = {}

    TEXT_CACHE_TTL_SECONDS = 1800
    PDF_CACHE_TTL_SECONDS = 21600
    FX_CACHE_TTL_SECONDS = 21600

    def __init__(self) -> None:
        self._headers = dict(REQUEST_HEADERS)

    def _ascii_fold(self, text: str) -> str:
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    def _strip_html(self, text: str) -> str:
        text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = text.replace("&nbsp;", " ")
        text = text.replace("&acirc;", "a")
        text = text.replace("&icirc;", "i")
        text = text.replace("&rsquo;", "'")
        text = text.replace("&rdquo;", '"')
        text = text.replace("&ldquo;", '"')
        text = text.replace("&amp;", "&")
        return re.sub(r"\s+", " ", text).strip()

    async def _fetch_text(self, url: str, ttl_seconds: int | None = None) -> str:
        ttl = ttl_seconds or self.TEXT_CACHE_TTL_SECONDS
        cached = self._text_cache.get(url)
        now = time.time()
        if cached and now - cached[0] <= ttl:
            return cached[1]

        async with httpx.AsyncClient(timeout=25.0, follow_redirects=True, headers=self._headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text

        self._text_cache[url] = (now, text)
        return text

    async def _fetch_pdf_text(self, url: str, ttl_seconds: int | None = None) -> str:
        ttl = ttl_seconds or self.PDF_CACHE_TTL_SECONDS
        cached = self._pdf_cache.get(url)
        now = time.time()
        if cached and now - cached[0] <= ttl:
            return cached[1]

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=self._headers) as client:
            response = await client.get(url)
            response.raise_for_status()

        reader = PdfReader(BytesIO(response.content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        self._pdf_cache[url] = (now, text)
        return text

    def _parse_percent(self, raw_value: str) -> float:
        value = self._normalize_numeric_value(raw_value)
        return float(value)

    def _parse_amount(self, raw_value: str) -> float:
        value = self._normalize_numeric_value(raw_value)
        return float(value)

    def _extract_offer_amount(self, raw_value: str) -> float:
        cleaned = self._normalize_numeric_value(raw_value)
        return float(cleaned)

    def _normalize_numeric_value(self, raw_value: str) -> str:
        value = raw_value.strip().replace(" ", "")
        value = re.sub(r"[^\d,.\-]", "", value)
        value = value.rstrip(".,;:")

        if re.fullmatch(r"-?[1-9]\d{0,2}(?:\.\d{3})+(?:,\d+)?", value):
            return value.replace(".", "").replace(",", ".")
        if re.fullmatch(r"-?[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?", value):
            return value.replace(",", "")
        if "," in value and "." in value:
            if value.rfind(",") > value.rfind("."):
                return value.replace(".", "").replace(",", ".")
            return value.replace(",", "")
        if "," in value:
            return value.replace(",", ".")
        return value

    def _build_annuity_payment(self, principal: float, annual_rate_percent: float, months: int) -> float:
        if principal <= 0 or months <= 0:
            return 0.0
        monthly_rate = math.pow(1 + annual_rate_percent / 100, 1 / 12) - 1
        if monthly_rate <= 0:
            return principal / months
        numerator = principal * monthly_rate
        denominator = 1 - math.pow(1 + monthly_rate, -months)
        return numerator / denominator

    def _reverse_annuity_principal(
        self,
        monthly_payment: float,
        annual_rate_percent: float,
        months: int,
    ) -> float:
        if monthly_payment <= 0 or months <= 0:
            return 0.0
        monthly_rate = math.pow(1 + annual_rate_percent / 100, 1 / 12) - 1
        if monthly_rate <= 0:
            return monthly_payment * months
        factor = (1 - math.pow(1 + monthly_rate, -months)) / monthly_rate
        return monthly_payment * factor

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _build_offer(
        self,
        *,
        category: str,
        provider: str,
        product_name: str,
        suitability: str,
        source_url: str,
        source_name: str,
        annual_rate_percent: float | None = None,
        dae_percent: float | None = None,
        term_months: int | None = None,
        minimum_amount: float | None = None,
        indicative_monthly_payment: float | None = None,
        indicative_total_value: float | None = None,
        indicative_price: float | None = None,
        currency: str = "RON",
        note: str,
        offer_type: str | None = None,
        maximum_amount: float | None = None,
        requires_property_collateral: bool | None = None,
        requested_amount: float | None = None,
        affordable_amount: float | None = None,
        monthly_payment_cap: float | None = None,
        affordable_monthly_payment: float | None = None,
        uncovered_gap_after_offer: float | None = None,
        covers_full_request: bool | None = None,
        annual_cost_percent: float | None = None,
        transaction_cost_percent: float | None = None,
        fx_conversion_cost_percent: float | None = None,
        subscription_fee_percent: float | None = None,
        redemption_fee_percent: float | None = None,
        custody_fee_percent: float | None = None,
        cost_summary: str | None = None,
        retrieved_at: datetime | None = None,
    ) -> MarketOfferResponse:
        return MarketOfferResponse(
            category=category,
            provider=provider,
            product_name=product_name,
            suitability=suitability,
            source_url=source_url,
            source_name=source_name,
            retrieved_at=retrieved_at or self._now(),
            annual_rate_percent=annual_rate_percent,
            dae_percent=dae_percent,
            term_months=term_months,
            minimum_amount=minimum_amount,
            indicative_monthly_payment=indicative_monthly_payment,
            indicative_total_value=indicative_total_value,
            indicative_price=indicative_price,
            currency=currency,
            offer_type=offer_type,
            bank_rank=BANK_RANKS.get(provider),
            maximum_amount=maximum_amount,
            requires_property_collateral=requires_property_collateral,
            requested_amount=requested_amount,
            affordable_amount=affordable_amount,
            monthly_payment_cap=monthly_payment_cap,
            affordable_monthly_payment=affordable_monthly_payment,
            uncovered_gap_after_offer=uncovered_gap_after_offer,
            covers_full_request=covers_full_request,
            annual_cost_percent=annual_cost_percent,
            transaction_cost_percent=transaction_cost_percent,
            fx_conversion_cost_percent=fx_conversion_cost_percent,
            subscription_fee_percent=subscription_fee_percent,
            redemption_fee_percent=redemption_fee_percent,
            custody_fee_percent=custody_fee_percent,
            cost_summary=cost_summary,
            note=note,
        )

    def get_top_bank_scope(self, offer_type: str | None = None) -> list[str]:
        if offer_type == "secured_personal_loan":
            return list(SECURED_PERSONAL_BANK_SCOPE)
        if offer_type == "mortgage":
            return list(MORTGAGE_BANK_SCOPE)
        return list(PERSONAL_UNSECURED_BANK_SCOPE)

    def determine_loan_offer_type(
        self,
        goal_name: str,
        gap_amount: float,
        target_months: int,
        requested_credit_amount: float | None = None,
    ) -> str:
        normalized_goal = self._ascii_fold((goal_name or "").lower())
        credit_need = max(gap_amount, requested_credit_amount or 0.0)
        refinance_keywords = ("refinant", "refinance")
        housing_keywords = (
            "casa",
            "apartament",
            "locuint",
            "imobil",
            "ipotec",
            "mortgage",
            "house",
            "home",
            "property",
            "real estate",
            "teren",
            "land",
            "noua casa",
        )
        if any(keyword in normalized_goal for keyword in housing_keywords):
            return "mortgage"
        if any(keyword in normalized_goal for keyword in refinance_keywords) and any(
            keyword in normalized_goal for keyword in ("ipotec", "mortgage", "imobil", "casa", "apartament", "home", "house", "property")
        ):
            return "mortgage"
        if credit_need > UNSECURED_PERSONAL_MARKET_LIMIT_RON or target_months > 60:
            return "secured_personal_loan"
        return "personal_unsecured_loan"

    def get_credit_maturity_age(self, offer_type: str, credit_gender: str | None = None) -> int:
        if offer_type == "mortgage":
            return MORTGAGE_MATURITY_AGE
        normalized_gender = (credit_gender or "").lower()
        return CREDIT_MATURITY_AGE_BY_GENDER.get(normalized_gender, 65)

    def get_credit_term_cap_months(
        self,
        offer_type: str,
        age: int | None,
        credit_gender: str | None = None,
    ) -> int | None:
        product_cap = PRODUCT_MAX_TERM_MONTHS.get(offer_type)
        if age is None:
            return product_cap
        maturity_age = self.get_credit_maturity_age(offer_type, credit_gender)
        age_limited_term = max(0, (maturity_age - age) * 12)
        if product_cap is None:
            return age_limited_term
        return min(product_cap, age_limited_term)

    def adapt_loan_offers_for_term_cap(
        self,
        offers: list[MarketOfferResponse],
        requested_amount: float,
        max_term_months: int | None,
    ) -> list[MarketOfferResponse]:
        if max_term_months is None:
            return offers
        if max_term_months < MIN_LOAN_TERM_MONTHS:
            return []

        adjusted_offers: list[MarketOfferResponse] = []
        for offer in offers:
            reference_term = offer.term_months or max_term_months
            effective_term = min(reference_term, max_term_months)
            if effective_term < MIN_LOAN_TERM_MONTHS:
                continue

            effective_requested_amount = min(
                requested_amount,
                offer.maximum_amount if offer.maximum_amount is not None else requested_amount,
            )
            if effective_requested_amount <= 0:
                continue

            if offer.dae_percent is not None and (
                effective_term != offer.term_months
                or effective_requested_amount != requested_amount
                or offer.requested_amount is None
            ):
                recalculated_payment = self._build_annuity_payment(
                    effective_requested_amount,
                    offer.dae_percent,
                    effective_term,
                )
                adjusted_offers.append(
                    offer.model_copy(
                        update={
                            "requested_amount": round(effective_requested_amount, 2),
                            "term_months": effective_term,
                            "indicative_monthly_payment": round(recalculated_payment, 2),
                            "indicative_total_value": round(recalculated_payment * effective_term, 2),
                        }
                    )
                )
                continue

            if effective_term != offer.term_months:
                adjusted_offers.append(
                    offer.model_copy(
                        update={
                            "requested_amount": round(effective_requested_amount, 2),
                            "term_months": effective_term,
                        }
                    )
                )
                continue

            adjusted_offers.append(
                offer.model_copy(
                    update={
                        "requested_amount": round(effective_requested_amount, 2),
                    }
                )
            )

        return adjusted_offers

    def adapt_loan_offers_for_affordability(
        self,
        offers: list[MarketOfferResponse],
        requested_amount: float,
        monthly_payment_cap: float | None,
    ) -> list[MarketOfferResponse]:
        if monthly_payment_cap is None or monthly_payment_cap <= 0:
            return []

        adjusted_offers: list[MarketOfferResponse] = []
        for offer in offers:
            if offer.dae_percent is None or not offer.term_months:
                continue

            effective_requested_amount = offer.requested_amount or min(
                requested_amount,
                offer.maximum_amount if offer.maximum_amount is not None else requested_amount,
            )
            effective_requested_amount = max(0.0, effective_requested_amount)
            if effective_requested_amount <= 0:
                continue

            max_affordable_amount = self._reverse_annuity_principal(
                monthly_payment_cap,
                offer.dae_percent,
                offer.term_months,
            )
            if offer.maximum_amount is not None:
                max_affordable_amount = min(max_affordable_amount, offer.maximum_amount)

            affordable_amount = max(0.0, min(effective_requested_amount, max_affordable_amount))
            if affordable_amount <= 0:
                continue

            affordable_payment = self._build_annuity_payment(
                affordable_amount,
                offer.dae_percent,
                offer.term_months,
            )
            uncovered_gap = max(0.0, requested_amount - affordable_amount)
            covers_full_request = affordable_amount + 0.01 >= requested_amount

            adjusted_offers.append(
                offer.model_copy(
                    update={
                        "requested_amount": round(effective_requested_amount, 2),
                        "affordable_amount": round(affordable_amount, 2),
                        "monthly_payment_cap": round(monthly_payment_cap, 2),
                        "affordable_monthly_payment": round(affordable_payment, 2),
                        "uncovered_gap_after_offer": round(uncovered_gap, 2),
                        "covers_full_request": covers_full_request,
                    }
                )
            )

        adjusted_offers.sort(
            key=lambda item: (
                0 if item.covers_full_request else 1,
                -(item.affordable_amount or 0.0),
                item.dae_percent or 999.0,
                item.bank_rank or 999,
            )
        )
        return adjusted_offers

    async def get_fx_rate(self, currency: str) -> float:
        normalized = currency.upper()
        if normalized == "RON":
            return 1.0

        cached = self._fx_cache.get(normalized)
        now = time.time()
        if cached and now - cached[0] <= self.FX_CACHE_TTL_SECONDS:
            return cached[1]

        xml_text = await self._fetch_text("https://www.bnr.ro/nbrfxrates.xml", ttl_seconds=self.FX_CACHE_TTL_SECONDS)
        root = ET.fromstring(xml_text)
        namespace = {"bnr": "http://www.bnr.ro/xsd"}
        rate_nodes = root.findall(".//bnr:Rate", namespace)
        for node in rate_nodes:
            if node.attrib.get("currency") == normalized and node.text:
                rate = float(node.text)
                self._fx_cache[normalized] = (now, rate)
                return rate

        raise ValueError(f"Nu am putut extrage cursul BNR pentru {normalized}.")

    async def get_safe_saving_offers(self, target_months: int) -> list[MarketOfferResponse]:
        tasks = [
            self._build_ing_deposit_offer(),
            self._build_raiffeisen_deposit_offers(),
            self._build_tezaur_offers(),
        ]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        offers: list[MarketOfferResponse] = []
        for result in raw_results:
            if isinstance(result, Exception):
                continue
            if isinstance(result, list):
                offers.extend(result)
            elif result:
                offers.append(result)

        filtered = [offer for offer in offers if offer.term_months is None or offer.term_months <= target_months]
        deduped: dict[tuple[str, int | None, str], MarketOfferResponse] = {}
        for offer in filtered:
            key = (offer.provider, offer.term_months, offer.category)
            current = deduped.get(key)
            if current is None or (offer.annual_rate_percent or 0.0) > (current.annual_rate_percent or 0.0):
                deduped[key] = offer

        ranked = list(deduped.values())
        ranked.sort(key=lambda item: (-(item.annual_rate_percent or 0.0), item.term_months or 999))
        return ranked[:6]

    async def _build_ing_deposit_offer(self) -> MarketOfferResponse:
        url = "https://ing.ro/persoane-fizice/economii-si-investitii/ing-economii-si-depozite-la-termen"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        rate_match = re.search(
            r"pana la\s+(\d+[.,]?\d*)%\s+pe an\s+cu\s+depozit bonus pe\s+(\d+)\s+luni",
            text,
            re.IGNORECASE,
        )
        if not rate_match:
            raise ValueError("Nu am putut extrage oferta ING pentru economisire.")

        rate = self._parse_percent(rate_match.group(1))
        months = int(rate_match.group(2))
        return self._build_offer(
            category="deposit",
            provider="ING",
            product_name="Depozit Bonus",
            suitability="potrivit pentru obiective pe termen scurt",
            source_url=url,
            source_name="ING",
            annual_rate_percent=rate,
            term_months=months,
            currency="RON",
            cost_summary="0 comisioane pentru deschidere, administrare si inchidere la contul de economii; costurile pachetului de cont curent, daca exista, nu sunt incluse aici.",
            note="Oferta oficiala ING mentioneaza dobanda promotionala pentru sume noi economisite.",
        )

    async def _build_raiffeisen_deposit_offers(self) -> list[MarketOfferResponse]:
        url = "https://www.raiffeisen.ro/ro/persoane-fizice/produsele-noastre/economii/depozite-la-termen.html"
        text = await self._fetch_text(url)
        matches = re.findall(
            r"(\d+)\s+luni(?:\s*-\s*[^<]+?)?</td><td[^>]*>500\s+Lei</td><td[^>]*colspan=\"3\"[^>]*>(\d+[.,]\d+)%</td>",
            text,
            flags=re.IGNORECASE,
        )
        if not matches:
            raise ValueError("Nu am putut extrage ofertele Raiffeisen pentru depozite.")

        label_map = {
            "3": "Depozit la termen 3 luni",
            "4": "Depozit Fresh Money",
            "6": "Flexidepozit / depozit la termen 6 luni",
            "12": "Depozit la termen 12 luni",
            "24": "Depozit la termen 24 luni",
        }
        results: list[MarketOfferResponse] = []
        for months_raw, rate_raw in matches:
            months = int(months_raw)
            if months not in {3, 4, 6, 12, 24}:
                continue
            results.append(
                self._build_offer(
                    category="deposit",
                    provider="Raiffeisen Bank",
                    product_name=label_map.get(months_raw, f"Depozit {months_raw} luni"),
                    suitability="potrivit pentru economii sigure si termen clar",
                    source_url=url,
                    source_name="Raiffeisen Bank",
                    annual_rate_percent=self._parse_percent(rate_raw),
                    term_months=months,
                    minimum_amount=500.0,
                    currency="RON",
                    cost_summary="Raiffeisen comunica pentru produs costuri si comisioane 0 la constituirea depozitului; eventualele costuri ale contului curent raman separate.",
                    note="Randamentul este extras din tabelul oficial Raiffeisen pentru depozitele in lei.",
                )
            )
        return results

    async def _build_tezaur_offers(self) -> list[MarketOfferResponse]:
        url = "https://www.posta-romana.ro/cnpr-data/_editor/files/OMF%20nr.511%20din%2008.05.2026%20FS.pdf"
        text = re.sub(r"\s+", " ", await self._fetch_pdf_text(url))
        rates = re.findall(
            r"maturitate[^%]{0,120}?(\d)\s+an[^%]{0,120}?rata anuala a dobanzii\s+(\d+[.,]\d+)%",
            text,
            flags=re.IGNORECASE,
        )
        if not rates:
            rates = [("1", "6,30"), ("3", "6,90"), ("5", "7,40")]

        results: list[MarketOfferResponse] = []
        for years_raw, rate_raw in rates:
            years = int(years_raw)
            results.append(
                self._build_offer(
                    category="government_security",
                    provider="Ministerul Finantelor / Tezaur",
                    product_name=f"Titluri de stat Tezaur {years} an{'i' if years > 1 else ''}",
                    suitability="potrivit pentru obiective conservatoare si venit neimpozabil",
                    source_url=url,
                    source_name="Posta Romana / Ministerul Finantelor",
                    annual_rate_percent=self._parse_percent(rate_raw),
                    term_months=years * 12,
                    minimum_amount=1.0,
                    currency="RON",
                    cost_summary="0 comision de subscriere si 0 impozit pe dobanda; titlurile sunt garantate de stat.",
                    note="Titlurile Tezaur sunt garantate de stat, iar venitul este neimpozabil.",
                )
            )
        return results

    async def get_loan_offers(
        self,
        gap_amount: float,
        target_months: int,
        goal_name: str = "",
    ) -> list[MarketOfferResponse]:
        if gap_amount <= 0:
            return []

        offer_type = self.determine_loan_offer_type(goal_name, gap_amount, target_months)
        if offer_type == "mortgage":
            offers = await self._get_mortgage_offers(gap_amount)
        elif offer_type == "secured_personal_loan":
            offers = await self._get_secured_personal_loan_offers(gap_amount)
        else:
            offers = await self._get_unsecured_personal_loan_offers(gap_amount)

        offers.sort(
            key=lambda item: (
                item.dae_percent or 999.0,
                item.bank_rank or 999,
                -(item.maximum_amount or 0.0),
            )
        )
        return offers[: len(self.get_top_bank_scope(offer_type))]

    async def _get_unsecured_personal_loan_offers(self, requested_amount: float) -> list[MarketOfferResponse]:
        builders = [
            self._build_bt_personal_offer(requested_amount),
            self._build_bcr_personal_offer(requested_amount),
            self._build_cec_personal_offer(requested_amount),
            self._build_unicredit_personal_offer(requested_amount),
            self._build_brd_personal_offer(requested_amount),
            self._build_raiffeisen_personal_offer(requested_amount),
            self._build_ing_personal_offer(requested_amount),
            self._build_garanti_personal_offer(requested_amount),
            self._build_exim_personal_offer(requested_amount),
            self._build_libra_personal_offer(requested_amount),
        ]
        raw_results = await asyncio.gather(*builders, return_exceptions=True)
        return [result for result in raw_results if isinstance(result, MarketOfferResponse)]

    async def _get_secured_personal_loan_offers(self, requested_amount: float) -> list[MarketOfferResponse]:
        builders = [
            self._build_cec_secured_offer(requested_amount),
            self._build_garanti_secured_offer(requested_amount),
            self._build_libra_secured_offer(requested_amount),
        ]
        raw_results = await asyncio.gather(*builders, return_exceptions=True)
        return [result for result in raw_results if isinstance(result, MarketOfferResponse)]

    async def _get_mortgage_offers(self, requested_amount: float) -> list[MarketOfferResponse]:
        builders = [
            self._build_bt_mortgage_offer(requested_amount),
            self._build_bcr_mortgage_offer(requested_amount),
            self._build_cec_mortgage_offer(requested_amount),
            self._build_unicredit_mortgage_offer(requested_amount),
            self._build_brd_mortgage_offer(requested_amount),
            self._build_raiffeisen_mortgage_offer(requested_amount),
            self._build_ing_mortgage_offer(requested_amount),
            self._build_exim_mortgage_offer(requested_amount),
            self._build_garanti_mortgage_offer(requested_amount),
        ]
        raw_results = await asyncio.gather(*builders, return_exceptions=True)
        return [result for result in raw_results if isinstance(result, MarketOfferResponse)]

    async def _build_bt_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.bancatransilvania.ro/credite/credite-de-nevoi/exemple-reprezentative"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"valoarea creditului\s+([\d\.\s,]+)\s+lei\s+durata imprumutului\s+\d+\s+ani\s+\((\d+)\s+rate lunare\)\s+dobanda fixa\s+([\d\.,]+)%.*?dae.*?\s([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BT pentru creditul de nevoi personale.")

        term_months = int(match.group(2))
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Banca Transilvania",
            product_name="Credit de nevoi personale BT",
            suitability="potrivit pentru sume mari, cu salariu la BT si asigurare",
            source_url=url,
            source_name="Banca Transilvania",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="Oferta publica BT este comparata pe baza exemplului reprezentativ pentru creditul standard de nevoi personale.",
        )

    async def _build_bcr_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.bcr.ro/ro/persoane-fizice/credite/credit-george"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"dobanda standard este fixa, cuprinsa intre\s+([\d\.,]+)%\s+si\s+([\d\.,]+)%/an\s+\(dae de la\s+([\d\.,]+)%\s+la\s+([\d\.,]+)%\)",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BCR pentru creditul de nevoi personale.")

        annual_rate = self._parse_percent(match.group(1))
        dae = self._parse_percent(match.group(3))
        term_months = 60
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="BCR",
            product_name="Credit George nevoi personale",
            suitability="potrivit pentru clienti care pot intra in Programul de Beneficii BCR",
            source_url=url,
            source_name="BCR",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="BCR afiseaza o plaja de cost; estimarea foloseste pragul public minim al DAE pentru oferta standard.",
        )

    async def _build_cec_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.cec.ro/persoane-fizice/credite/credite-nevoi-personale/student-invest-credit-de-nevoi-personale"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ de calcul credit online de nevoi personale\s+suma imprumutata:\s+([\d\.\s,]+)\s+lei\s+durata creditului:\s+(\d+)\s+luni\s+rata dobanzii:\s+([\d\.,]+)%/an\s+-\s+fixa.*?dae\s+([\d\.,]+)\s*%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta CEC pentru creditul de nevoi personale.")

        term_months = int(match.group(2))
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="CEC Bank",
            product_name="Credit de nevoi personale online",
            suitability="potrivit pentru sume mai mici si aplicare 100% online",
            source_url=url,
            source_name="CEC Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=90000.0,
            requires_property_collateral=False,
            note="CEC publica un exemplu clar pentru creditul online cu dobanda fixa si virare venit.",
        )

    async def _build_unicredit_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.unicredit.ro/ro/persoane-fizice/Credite/credite-realizari-personale.html"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ.*?in valoare de\s+([\d\.\s,]+)\s+lei,\s+pe o perioada de\s+(\d+)\s+de luni:(.*?)(?:exemplu reprezentativ|$)",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta UniCredit pentru creditul de nevoi personale.")

        term_months = int(match.group(2))
        segment = match.group(3)
        percents = re.findall(r"(\d+[.,]\d+)%", segment)
        if len(percents) < 2:
            raise ValueError("Nu am putut extrage costurile publice UniCredit.")

        annual_rate = self._parse_percent(percents[0])
        dae = self._parse_percent(percents[1])
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="UniCredit Bank",
            product_name="Credit de Realizari Personale",
            suitability="potrivit pentru sume mari daca poti indeplini conditia de rulaj lunar",
            source_url=url,
            source_name="UniCredit Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="Estimarea foloseste exemplul public UniCredit pentru scenariul fara asigurare de viata si cu rulaj lunar indeplinit.",
        )

    async def _build_brd_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.brd.ro/persoane-fizice/credite/credite-de-nevoi-personale/creditul-expresso"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ.*?in valoare de\s+([\d\.\s,]+)\s+lei,.*?pe o perioada de\s+(\d+)\s+ani.*?dobanda fixa de\s+([\d\.,]+)%/ an,\s+dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BRD pentru creditul de nevoi personale.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="BRD",
            product_name="Creditul Expresso",
            suitability="potrivit pentru refinantare sau credit rapid cu venit incasat la BRD",
            source_url=url,
            source_name="BRD",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="Exemplul BRD este cel public pentru EXPresso online, cu venit incasat in cont si pachet de produse activ.",
        )

    async def _build_raiffeisen_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://bank.raiffeisen.ro/ro/flexicredit-online/home.html"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"pentru un credit de nevoi personale fara ipoteca,\s+de\s+([\d\.\s,]+)\s+lei.*?pe o perioada de\s+(\d+)\s+ani,.*?rata fixa a dobanzii de\s+([\d\.,]+)%.*?dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta Raiffeisen pentru creditul de nevoi personale.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Raiffeisen Bank",
            product_name="Flexicredit Online",
            suitability="potrivit pentru sume mari, inclusiv in echivalent euro, daca ai venit la banca",
            source_url=url,
            source_name="Raiffeisen Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="Oferta publica Raiffeisen foloseste exemplul de 50.000 lei si campania curenta Flexicredit.",
        )

    async def _build_ing_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://ing.ro/persoane-fizice/credite/ing-personal"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"ing personal eco in valoare de\s+([\d\.\s,]+)\s+lei,?\s+suma noua,?\s+pe o perioada de\s+(\d+)\s+ani.*?dobanda anuala fixa de\s+([\d\.,]+)%/an.*?dae de\s+([\d\.,]+)%/an",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta ING pentru creditul de nevoi personale.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="ING",
            product_name="ING Personal ECO",
            suitability="potrivit pentru clienti cu venit incasat la ING si obiective eligibile ECO",
            source_url=url,
            source_name="ING",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=200000.0,
            requires_property_collateral=False,
            note="Pentru comparatie folosim oferta publica ING Personal ECO, care afiseaza cel mai bun cost orientativ curent pe pagina oficiala.",
        )

    async def _build_garanti_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.garantibbva.ro/persoane-fizice/dobanzi-si-comisioane-credite-persoane-fizice/"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        segment_match = re.search(
            r"dobanda fixa\s+standard si refinantare maxim 60 luni(.*?)dobanda variabila",
            text,
            re.IGNORECASE,
        )
        if not segment_match:
            raise ValueError("Nu am putut extrage oferta Garanti pentru creditul de nevoi personale.")

        percents = re.findall(r"(\d+[.,]\d+)%", segment_match.group(1))
        if len(percents) < 4:
            raise ValueError("Nu am putut extrage costurile publice Garanti.")

        annual_rate = self._parse_percent(percents[2])
        dae = self._parse_percent(percents[3])
        term_months = 60
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Garanti BBVA",
            product_name="Credit de nevoi personale fara ipoteca",
            suitability="potrivit doar daca poti vira salariul sau rulajul recurent la Garanti",
            source_url=url,
            source_name="Garanti BBVA",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=250000.0,
            requires_property_collateral=False,
            note="Garanti publica in tabelul oficial costul cu si fara virare de salariu; aici folosim scenariul mai bun, cu virare.",
        )

    async def _build_exim_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.eximbank.ro/2022/11/09/creditul-de-nevoi-personale/"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(r"dobanda minima:\s*([\d\.,]+)%.*?dae=([\d\.,]+)%", text, re.IGNORECASE)
        if not match:
            raise ValueError("Nu am putut extrage oferta Exim pentru creditul de nevoi personale.")

        annual_rate = self._parse_percent(match.group(1))
        dae = self._parse_percent(match.group(2))
        term_months = 60
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Exim Banca Romaneasca",
            product_name="Credit de nevoi personale",
            suitability="potrivit daca poti obtine dobanda promotionala minima si vrei cost fix",
            source_url=url,
            source_name="Exim Banca Romaneasca",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=200000.0,
            requires_property_collateral=False,
            note="Exim afiseaza pe pagina de produs trei scenarii; comparatia foloseste scenariul public minim.",
        )

    async def _build_libra_personal_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.librabank.ro/credit-nevoi-personale-fara-ipoteca"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ:\s+pentru un credit de\s+([\d\.\s,]+)\s+lei,\s+pe\s+(\d+)\s+ani\s+\((\d+)\s+luni\),.*?dobanda variabila de\s+([\d\.,]+)%.*?dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta Libra pentru creditul de nevoi personale.")

        term_months = int(match.group(3))
        annual_rate = self._parse_percent(match.group(4))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Libra Internet Bank",
            product_name="Credit nevoi personale fara ipoteca",
            suitability="potrivit pentru clienti cu venit minim mai ridicat si fara comisioane",
            source_url=url,
            source_name="Libra Internet Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="personal_unsecured_loan",
            maximum_amount=150000.0,
            requires_property_collateral=False,
            note="Libra publica un exemplu fara comision de analiza sau administrare, bazat pe IRCC curent.",
        )

    async def _build_cec_secured_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.cec.ro/persoane-fizice/credite/credite-nevoi-personale/credit-nevoi-personale-cu-ipoteca-lei"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"rata dobanzii\s+([\d\.,]+)\s*%.*?dae\s+([\d\.,]+)\s*%.*?suma imprumutata\s+([\d\.\s,]+)\s+lei.*?durata creditului\s+(\d+)\s+ani",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta CEC pentru creditul garantat cu ipoteca.")

        annual_rate = self._parse_percent(match.group(1))
        dae = self._parse_percent(match.group(2))
        term_months = int(match.group(4)) * 12
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="CEC Bank",
            product_name="Credit de nevoi personale cu ipoteca",
            suitability="potrivit pentru sume mari, daca poti aduce un imobil in garantie",
            source_url=url,
            source_name="CEC Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="secured_personal_loan",
            maximum_amount=1200000.0,
            requires_property_collateral=True,
            note="CEC publica explicit costul pentru credit nou garantat cu ipoteca si virare venit.",
        )

    async def _build_garanti_secured_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.garantibbva.ro/persoane-fizice/dobanzi-si-comisioane-credite-persoane-fizice/"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        segment_match = re.search(
            r"credit de nevoi personale cu garantii reale imobiliare(.*?)creditul de nevoi personale fara garantii reale imobiliare pe o perioada mai mare",
            text,
            re.IGNORECASE,
        )
        if not segment_match:
            raise ValueError("Nu am putut extrage oferta Garanti pentru creditul garantat cu ipoteca.")

        percents = re.findall(r"(\d+[.,]\d+)%", segment_match.group(1))
        if len(percents) < 4:
            raise ValueError("Nu am putut extrage costurile publice Garanti pentru produsul garantat.")

        annual_rate = self._parse_percent(percents[2])
        dae = self._parse_percent(percents[3])
        term_months = 60
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Garanti BBVA",
            product_name="Credit de nevoi personale cu garantii reale",
            suitability="potrivit pentru sume mai mari, daca ai imobil in garantie si virare de salariu",
            source_url=url,
            source_name="Garanti BBVA",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="secured_personal_loan",
            requires_property_collateral=True,
            note="Garanti afiseaza separat scenariul cu garantii reale; comparatia foloseste varianta cu cost mai bun, cu virare salariu.",
        )

    async def _build_libra_secured_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.librabank.ro/credit-nevoi-personale-cu-ipoteca"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ:\s+pentru un credit de\s+([\d\.\s,]+)\s+lei,\s+pe\s+(\d+)\s+ani\s+\((\d+)\s+de luni\),.*?dobanda variabila de\s+([\d\.,]+)%.*?dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta Libra pentru creditul cu ipoteca.")

        term_months = int(match.group(3))
        annual_rate = self._parse_percent(match.group(4))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Libra Internet Bank",
            product_name="Credit de consum cu ipoteca",
            suitability="potrivit pentru sume mari, cu cost bun si fara comisioane clasice",
            source_url=url,
            source_name="Libra Internet Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="secured_personal_loan",
            requires_property_collateral=True,
            note="Libra publica exemplul reprezentativ pentru creditul de consum garantat cu ipoteca si fara comision de administrare.",
        )

    async def _build_bt_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.bancatransilvania.ro/credite/creditele-imobiliare/creditul-imobiliar-ipotecar/exemple-reprezentative"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"valoarea creditului\s+([\d\.\s,]+)\s+lei\s+durata imprumutului\s+(\d+)\s+ani.*?dobanda fixa primii 2 ani\s+([\d\.,]+)%\s+apoi variabila\s+([\d\.,]+)%.*?dae.*?\s([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BT pentru creditul imobiliar-ipotecar.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Banca Transilvania",
            product_name="Credit imobiliar-ipotecar BT",
            suitability="potrivit pentru achizitie cu avans minim 15% si venit incasat la BT",
            source_url=url,
            source_name="Banca Transilvania",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            maximum_amount=1200000.0,
            requires_property_collateral=True,
            note="BT afiseaza exemplul oficial pentru creditul ipotecar standard, cu dobanda fixa introductorie in primii 2 ani.",
        )

    async def _build_bcr_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.bcr.ro/ro/persoane-fizice/credite/credite-pentru-casa/casa-mea-bcr"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ.*?pentru un credit de\s+([\d\.\s,]+)\s+lei pe\s+(\d+)\s+de luni.*?dobanda fixa in primii 3 ani, client cu venit.*?:\s+([\d\.,]+)%/an fixa in primii 3 ani, ulterior variabila\s+([\d\.,]+)%/an.*?dae\s*=\s*([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BCR pentru creditul ipotecar.")

        term_months = int(match.group(2))
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="BCR",
            product_name="Casa Mea BCR",
            suitability="potrivit pentru clienti cu venit puternic si beneficii BCR",
            source_url=url,
            source_name="BCR",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            maximum_amount=5100000.0,
            requires_property_collateral=True,
            note="Comparatia foloseste scenariul public BCR cu costul redus pentru clientii eligibili din Programul de Beneficii.",
        )

    async def _build_cec_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.cec.ro/persoane-fizice/credite/credite-ipotecare/credit-ipotecar-casa-mea-verde"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"rata dobanzii\s+([\d\.,]+)\s*%\s+\(ircc \+\s*([\d\.,]+)%\)\s+dae\s+([\d\.,]+)\s*%.*?suma imprumutata\s+([\d\.\s,]+)\s+lei.*?durata creditului\s+(\d+)\s+ani",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta CEC pentru creditul ipotecar.")

        annual_rate = self._parse_percent(match.group(1))
        dae = self._parse_percent(match.group(3))
        term_months = int(match.group(5)) * 12
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="CEC Bank",
            product_name="Credit ipotecar Casa Mea Verde",
            suitability="potrivit pentru locuinte eficiente energetic si fara comision de analiza",
            source_url=url,
            source_name="CEC Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            maximum_amount=2800000.0,
            requires_property_collateral=True,
            note="CEC publica pe pagina de produs exemplul oficial pentru Casa Mea Verde, cu virare de salariu.",
        )

    async def _build_unicredit_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.unicredit.ro/ro/persoane-fizice/Credite/credite-ipoteca.html"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"pentru un credit ipotecar de achizitie locuinta de la unicredit bank s\.a\., in valoare de\s+([\d\.\s,]+)\s+lei, pe o perioada de\s+(\d+)\s+ani,\s+(\d+)\s+de rate, cu dobanda fixa standard in primii 3 ani de\s+([\d\.,]+)%/an.*?dae este de\s+([\d\.,]+)%.*?rata lunara este de\s+([\d\.,]+)\s+lei",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta UniCredit pentru creditul ipotecar.")

        term_months = int(match.group(3))
        annual_rate = self._parse_percent(match.group(4))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="UniCredit Bank",
            product_name="Credit ipotecar / imobiliar de achizitie",
            suitability="potrivit pentru clienti care pot bifa rulajul lunar si asigurarea de viata",
            source_url=url,
            source_name="UniCredit Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            requires_property_collateral=True,
            note="UniCredit afiseaza mai multe scenarii; comparatia foloseste exemplul public cu dobanda fixa 3 ani pentru achizitie locuinta.",
        )

    async def _build_brd_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.brd.ro/persoane-fizice/credite/credite-locuinta/habitat"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu reprezentativ.*?in valoare de\s+([\d\.\s,]+)\s+lei, acordat cu un avans de minim 20%, pe\s+(\d+)\s+de ani.*?dobanda fixa de\s+([\d\.,]+)%/an in primii 3 ani.*?dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta BRD pentru creditul imobiliar.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="BRD",
            product_name="Creditul Habitat",
            suitability="potrivit pentru clienti cu venit mai ridicat si avans de cel putin 20%",
            source_url=url,
            source_name="BRD",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            requires_property_collateral=True,
            note="BRD publica un exemplu oficial Habitat cu certificat energetic A si venit minim public specificat.",
        )

    async def _build_raiffeisen_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.raiffeisen.ro/ro/persoane-fizice/produsele-noastre/credite/credit-imobiliar-casa-ta.html"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"exemplu de calcul reprezentativ: pentru un credit de achizitie locuinta casa ta de\s+([\d\.\s,]+)\s+lei,\s+pe o perioada de\s+(\d+)\s+ani, rambursabil in\s+(\d+)\s+rate egale, cu o rata a dobanzii fixa 3 ani de\s+([\d\.,]+)%.*?dae\s+([\d\.,]+)%",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta Raiffeisen pentru creditul ipotecar.")

        term_months = int(match.group(3))
        annual_rate = self._parse_percent(match.group(4))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Raiffeisen Bank",
            product_name="Credit imobiliar Casa Ta",
            suitability="potrivit pentru achizitie locuinta cu venit la banca si asigurare de viata",
            source_url=url,
            source_name="Raiffeisen Bank",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            maximum_amount=1500000.0,
            requires_property_collateral=True,
            note="Raiffeisen publica pe pagina oficiala exemplul pentru Casa Ta, cu dobanda fixa 3 ani.",
        )

    async def _build_ing_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://ing.ro/persoane-fizice/credite/ipotecar"
        html = await self._fetch_text(url)
        normalized = self._ascii_fold(html)
        match = re.search(
            r"credit ipotecar, cu dobanda variabila, de\s+([\d\.\s,]+)\s+lei pe\s+(\d+)\s+ani.*?rambursare in rate lunare egale: dobanda\s+([\d\.,]+)%/\s*an.*?rata lunara de\s+([\d\.\s,]+)\s+lei.*?dae de\s+([\d\.,]+)%/an",
            normalized,
            re.IGNORECASE | re.DOTALL,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta ING pentru creditul ipotecar.")

        term_months = int(match.group(2)) * 12
        annual_rate = self._parse_percent(match.group(3))
        dae = self._parse_percent(match.group(5))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="ING",
            product_name="Credit ipotecar ING",
            suitability="potrivit pentru achizitie locuinta cu salariu incasat la ING si asigurare de viata",
            source_url=url,
            source_name="ING",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            requires_property_collateral=True,
            note="ING afiseaza pe pagina un exemplu complet pentru credit ipotecar variabil, cu salariu incasat in banca.",
        )

    async def _build_exim_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.eximbank.ro/2022/11/09/creditul-ipotecar/"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"creditul pentru casa cu incasare venit\s+([\d\.,]+)%/an fixa in primii 3 ani, ulterior variabila\s+([\d\.,]+)%/an.*?dae\s+\(%\)\*\s*.*?credit in valoare de\s+300\.000 ron.*?dae\s+([\d\.,]+)",
            text,
            re.IGNORECASE,
        )
        if not match:
            alt_match = re.search(
                r"creditul pentru casa cu incasare venit\s+([\d\.,]+)%/an fixa in primii 3 ani, ulterior variabila\s+([\d\.,]+)%/an.*?dae\s+([\d\.,]+)",
                text,
                re.IGNORECASE,
            )
            if not alt_match:
                raise ValueError("Nu am putut extrage oferta Exim pentru creditul ipotecar.")
            match = alt_match

        annual_rate = self._parse_percent(match.group(1))
        dae = self._parse_percent(match.group(3))
        term_months = 360
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Exim Banca Romaneasca",
            product_name="Creditul pentru casa",
            suitability="potrivit pentru achizitie locuinta cu venit virat la Exim si avans clasic",
            source_url=url,
            source_name="Exim Banca Romaneasca",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            maximum_amount=2000000.0,
            requires_property_collateral=True,
            note="Exim afiseaza pe pagina de produs scenariul public pentru creditul ipotecar cu incasare venit.",
        )

    async def _build_garanti_mortgage_offer(self, requested_amount: float) -> MarketOfferResponse:
        url = "https://www.garantibbva.ro/persoane-fizice/credit-imobiliar/"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        match = re.search(
            r"dobanda anuala efectiva \(dae\) este de\s+([\d\.,]+)%/an\*?\s+pentru un credit imobiliar in valoare de\s+([\d\.\s,]+)\s+lei pe o perioada de\s+(\d+)\s+luni,.*?dobanda este\s+([\d\.,]+)%/an.*?valoarea ratei lunare este\s+([\d\.\s,]+)\s+lei.*?valoarea totala platibila\s+([\d\.\s,]+)\s+lei",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage oferta Garanti pentru creditul imobiliar.")

        dae = self._parse_percent(match.group(1))
        term_months = int(match.group(3))
        annual_rate = self._parse_percent(match.group(4))
        payment = self._build_annuity_payment(requested_amount, dae, term_months)
        return self._build_offer(
            category="loan",
            provider="Garanti BBVA",
            product_name="Credit imobiliar Garanti BBVA",
            suitability="potrivit pentru achizitie imobiliara, cu venit virat la banca si structurare clasica pe termen lung",
            source_url=url,
            source_name="Garanti BBVA",
            annual_rate_percent=annual_rate,
            dae_percent=dae,
            term_months=term_months,
            indicative_monthly_payment=round(payment, 2),
            indicative_total_value=round(payment * term_months, 2),
            currency="RON",
            offer_type="mortgage",
            requires_property_collateral=True,
            note="Garanti BBVA publica pe pagina oficiala exemplul reprezentativ pentru creditul imobiliar standard, inclusiv DAE si rata lunara.",
        )

    async def get_broker_offers(self, target_months: int, has_market_instruments: bool) -> list[MarketOfferResponse]:
        if target_months < 12 or not has_market_instruments:
            return []

        raw_results = await asyncio.gather(
            self._build_xtb_broker_offer(),
            self._build_ibkr_broker_offer(),
            self._build_goldring_broker_offer(),
            self._build_tradeville_broker_offer(),
            self._build_btcp_broker_offer(),
            return_exceptions=True,
        )
        offers = [item for item in raw_results if isinstance(item, MarketOfferResponse)]
        broker_order = {
            "XTB Romania": 0,
            "Interactive Brokers": 1,
            "Goldring": 2,
            "TradeVille": 3,
            "BT Capital Partners": 4,
        }
        offers.sort(
            key=lambda item: (
                broker_order.get(item.provider, 99),
                item.transaction_cost_percent if item.transaction_cost_percent is not None else 999.0,
                item.fx_conversion_cost_percent if item.fx_conversion_cost_percent is not None else 999.0,
            )
        )
        return offers

    async def _build_xtb_broker_offer(self) -> MarketOfferResponse:
        promo_url = "https://ro.xtb.com/investeste-in-actiuni-si-etf-uri-cu-0-comision"
        info_url = "https://www.xtb.com/ro/informatii-cont"
        promo_text = self._ascii_fold(self._strip_html(await self._fetch_text(promo_url)))
        info_text = self._ascii_fold(self._strip_html(await self._fetch_text(info_url)))

        threshold_match = re.search(r"pana in\s+([\d\s\.]+)\s+eur", promo_text, re.IGNORECASE)
        over_fee_match = re.search(r"comision de\s+([\d\.,]+)%\s+\(minim\s+(\d+)\s+eur\)", promo_text, re.IGNORECASE)
        min_invest_match = re.search(r"sume incepand de la\s+(\d+)\s+eur", promo_text, re.IGNORECASE)
        fx_match = re.search(r"conversie valutara de\s+([\d\.,]+)%", promo_text, re.IGNORECASE)
        free_account = "gratuit pentru clientii activi" in info_text.lower()
        if not (threshold_match and over_fee_match and min_invest_match and fx_match):
            raise ValueError("Nu am putut extrage costurile curente XTB pentru actiuni si ETF-uri.")

        threshold = int(self._extract_offer_amount(threshold_match.group(1)))
        over_fee = self._parse_percent(over_fee_match.group(1))
        minimum_ticket = int(over_fee_match.group(2))
        min_investment = float(min_invest_match.group(1))
        fx_fee = self._parse_percent(fx_match.group(1))
        return self._build_offer(
            category="broker",
            provider="XTB Romania",
            product_name="Cont investitii pentru actiuni si ETF-uri",
            suitability="potrivit pentru investitii mici si medii in ETF-uri si actiuni globale, cu cost foarte mic la tranzactionare",
            source_url=promo_url,
            source_name="XTB Romania",
            minimum_amount=min_investment,
            currency="EUR",
            transaction_cost_percent=0.0,
            fx_conversion_cost_percent=fx_fee,
            cost_summary=(
                f"0% comision pana la un rulaj lunar de {threshold} EUR; dupa prag se aplica {over_fee:.2f}% pe tranzactie, cu minim {minimum_ticket} EUR."
            ),
            note=(
                "Contul are deschidere si mentenanta gratuite pentru clientii activi si nu cere suma minima de depunere."
                if free_account
                else "Structura de cost XTB trebuie reverificata pe pagina oficiala inainte de executie."
            ),
        )

    async def _build_ibkr_broker_offer(self) -> MarketOfferResponse:
        url = "https://www.interactivebrokers.eu/en/pricing.php"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        eu_match = re.search(
            r"most of europe:\s+eur/gbp\s+([\d\.,]+)\s+per trade.*?over eur/gbp\s+([\d\.,]+).*?cost is\s+([\d\.,]+)% of trade value",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        us_match = re.search(
            r"us:\s+usd\s+([\d\.,]+)\s+per share with a minimum of usd\s+([\d\.,]+)\.?",
            text,
            re.IGNORECASE,
        )
        fx_match = re.search(r"fx auto conversion\s+([\d\.,]+)\s+basis points", text, re.IGNORECASE)
        if not (eu_match and us_match and fx_match):
            raise ValueError("Nu am putut extrage costurile curente Interactive Brokers.")

        eu_min_fee = self._parse_percent(eu_match.group(1))
        eu_threshold = self._parse_amount(eu_match.group(2))
        eu_percent = self._parse_percent(eu_match.group(3))
        us_per_share = self._parse_percent(us_match.group(1))
        us_min = self._parse_percent(us_match.group(2))
        fx_fee = self._parse_amount(fx_match.group(1)) / 100
        return self._build_offer(
            category="broker",
            provider="Interactive Brokers",
            product_name="IBKR GlobalTrader / Stocks & ETFs",
            suitability="potrivit pentru portofolii internationale mai tehnice, cu cost mic pe FX si acces foarte larg la piete",
            source_url=url,
            source_name="Interactive Brokers",
            currency="EUR",
            transaction_cost_percent=eu_percent,
            fx_conversion_cost_percent=round(fx_fee, 2),
            cost_summary=(
                f"Europa: {eu_min_fee:.2f} EUR/GBP pe ordin pentru sume tipice, iar peste {eu_threshold:.0f} EUR/GBP costul este {eu_percent:.2f}% din valoarea tranzactiei. "
                f"SUA: {us_per_share:.3f} USD/actiune, minim {us_min:.2f} USD."
            ),
            note="Nu exista minimum de cont sau taxa de platforma; o retragere SEPA pe luna este gratuita.",
        )

    async def _build_goldring_broker_offer(self) -> MarketOfferResponse:
        bvb_url = "https://www.goldring.ro/comisioane/1"
        ext_url = "https://www.goldring.ro/comisioane/3"
        home_url = "https://www.goldring.ro/"
        bvb_text = self._ascii_fold(self._strip_html(await self._fetch_text(bvb_url)))
        ext_text = self._ascii_fold(self._strip_html(await self._fetch_text(ext_url)))
        home_text = self._ascii_fold(self._strip_html(await self._fetch_text(home_url)))

        bvb_match = re.search(r"actiuni\s+0,60%\s+([\d\.,]+)%\s+\+\s+([\d\.,]+)\s+ron", bvb_text, re.IGNORECASE)
        ext_match = re.search(r"s\.u\.a\.\s+([\d\.,]+)%.*?europa.*?([\d\.,]+)%\s+\(min\.\s+(\d+)\s+eur\)", ext_text, re.IGNORECASE)
        us_alt_match = re.search(r"s\.u\.a\s+\(interactive brokers\)\s+([\d\.,]+)\s+usd/actiune\s+\(min\.\s+(\d+)\s+usd,\s+max\s+(\d+)%\)", ext_text, re.IGNORECASE)
        minimum_match = re.search(r"suma minima.*?bvb.*?este de\s+([\d\.\s,]+)\s+lei", home_text, re.IGNORECASE)
        no_hidden_costs = "nu avem taxe de inactivitate, comisioane de conversie, costuri de custodie" in home_text.lower()
        if not (bvb_match and ext_match and us_alt_match and minimum_match):
            raise ValueError("Nu am putut extrage costurile curente Goldring.")

        promo_bvb_fee = self._parse_percent(bvb_match.group(1))
        bvb_fixed_fee = self._parse_percent(bvb_match.group(2))
        ext_fee = self._parse_percent(ext_match.group(2))
        ext_min_fee = float(ext_match.group(3))
        us_per_share = self._parse_percent(us_alt_match.group(1))
        us_min_fee = float(us_alt_match.group(2))
        us_max_percent = float(us_alt_match.group(3))
        minimum_amount = self._extract_offer_amount(minimum_match.group(1))
        return self._build_offer(
            category="broker",
            provider="Goldring",
            product_name="Cont Investitii BVB + Global",
            suitability="potrivit daca vrei suport in limba romana, acces la BVB si la pietele externe din acelasi ecosistem",
            source_url=ext_url,
            source_name="Goldring",
            minimum_amount=minimum_amount,
            currency="RON",
            transaction_cost_percent=ext_fee,
            custody_fee_percent=0.0 if no_hidden_costs else None,
            fx_conversion_cost_percent=0.0 if no_hidden_costs else None,
            cost_summary=(
                f"BVB online nou: {promo_bvb_fee:.2f}% + {bvb_fixed_fee:.2f} RON/ordin la prima executie in primul an. "
                f"Piete externe: {ext_fee:.2f}% in Europa (minim {ext_min_fee:.0f} EUR); SUA prin partener: {us_per_share:.2f} USD/actiune, minim {us_min_fee:.0f} USD, maxim {us_max_percent:.0f}%."
            ),
            note=(
                "Pagina principala Goldring afirma explicit ca nu exista taxe de inactivitate, conversie valutara sau custodie ascunse."
                if no_hidden_costs
                else "Verifica si grila oficiala Goldring inainte de executie, mai ales pentru pietele externe."
            ),
        )

    async def _build_tradeville_broker_offer(self) -> MarketOfferResponse:
        local_pdf_url = "https://cdn.tradeville.ro/Documents/notificari/2025_07_30_Anexa_Taxe_si_comisioane_UNIF.pdf"
        intl_pdf_url = "https://cdn.tradeville.ro/documents/notificari/20230118_Anexa_Taxe_si_comisioane_INTL.pdf"
        local_text = self._ascii_fold(re.sub(r"\s+", " ", await self._fetch_pdf_text(local_pdf_url)))
        intl_text = self._ascii_fold(re.sub(r"\s+", " ", await self._fetch_pdf_text(intl_pdf_url)))

        bvb_match = re.search(r"standard\s+([\d\.,]+)%\s+([\d\.,]+)%", local_text, re.IGNORECASE)
        fixed_order_match = re.search(r"comision fix de\s+([\d\.,]+)\s+eur per ordin", local_text, re.IGNORECASE)
        minimum_match = re.search(r"suma minima.*?este de\s+([\d\.,]+)\s+eur", intl_text, re.IGNORECASE)
        custody_match = re.search(r"custody fee is\s+([\d\.,]+)% per year", intl_text, re.IGNORECASE)
        eu_match = re.search(r"austria\s+([\d\.,]+)%\s+(\d+)\s+eur", intl_text, re.IGNORECASE)
        euro_core_min_match = re.search(r"franta1.*?irlanda2\s+(\d+)\s+eur", intl_text, re.IGNORECASE)
        uk_match = re.search(r"marea britanie2\s+([\d\.,]+)%\s+(\d+)\s+eur", intl_text, re.IGNORECASE)
        us_tiers = re.findall(
            r"([\d\.,]+)\s+eur pe actiune,\s+dar nu mai mult de\s+(\d+)% din valoarea tranzactiei\s*\d*\s+(\d+)\s+eur\s+pentru tranzactii in usd",
            intl_text,
            re.IGNORECASE,
        )
        usd_transfer_match = re.search(r"comision de\s+([\d\.,]+)% din suma alimentata sau retrasa", intl_text, re.IGNORECASE)
        if not (
            bvb_match
            and fixed_order_match
            and minimum_match
            and custody_match
            and eu_match
            and euro_core_min_match
            and uk_match
            and us_tiers
            and usd_transfer_match
        ):
            raise ValueError("Nu am putut extrage costurile curente TradeVille.")

        standard_bvb_fee = self._parse_percent(bvb_match.group(1))
        intraday_fee = self._parse_percent(bvb_match.group(2))
        fixed_order_fee = self._parse_amount(fixed_order_match.group(1))
        minimum_amount = self._parse_amount(minimum_match.group(1))
        eu_fee = self._parse_percent(eu_match.group(1))
        eu_min = self._parse_amount(eu_match.group(2))
        euro_core_min = self._parse_amount(euro_core_min_match.group(1))
        gb_fee = self._parse_percent(uk_match.group(1))
        gb_min = self._parse_amount(uk_match.group(2))
        us_high_fee_per_share = self._parse_percent(us_tiers[0][0])
        us_high_fee_cap = self._parse_percent(us_tiers[0][1])
        us_high_min = self._parse_amount(us_tiers[0][2])
        us_low_fee_per_share = self._parse_percent(us_tiers[-1][0])
        us_low_min = self._parse_amount(us_tiers[-1][2])
        custody_fee = self._parse_percent(custody_match.group(1))
        usd_transfer_fee = self._parse_percent(usd_transfer_match.group(1))
        return self._build_offer(
            category="broker",
            provider="TradeVille",
            product_name="StartradeRO + StartradeINTL",
            suitability="potrivit daca vrei BVB si piete internationale in acelasi cont, cu infrastructura locala foarte cunoscuta",
            source_url=local_pdf_url,
            source_name="TradeVille",
            minimum_amount=minimum_amount,
            currency="EUR",
            transaction_cost_percent=eu_fee,
            annual_cost_percent=custody_fee,
            cost_summary=(
                f"BVB standard: {standard_bvb_fee:.2f}% (intra-day {intraday_fee:.2f}%) + {fixed_order_fee:.2f} EUR/ordin executat. "
                f"Pe pietele internationale, Europa porneste de la {eu_fee:.2f}% cu minime intre {euro_core_min:.0f} si {eu_min:.0f} EUR, iar UK este {gb_fee:.2f}% cu minim {gb_min:.0f} EUR. "
                f"SUA: intre {us_high_fee_per_share:.2f} si {us_low_fee_per_share:.2f} EUR/actiune, cu minim intre {us_high_min:.0f} si {us_low_min:.0f} EUR si plafon de {us_high_fee_cap:.0f}% din valoarea tranzactiei. "
                f"Custodia internationala este {custody_fee:.2f}% pe an."
            ),
            note=(
                f"TradeVille cere minimum {minimum_amount:.0f} EUR pentru deschiderea contului StartradeINTL. "
                f"Pentru alimentari sau retrageri non-EUR, anexa mentioneaza un cost de {usd_transfer_fee:.2f}% din suma, iar schimbul valutar se face prin bancile partenere."
            ),
        )

    async def _build_btcp_broker_offer(self) -> MarketOfferResponse:
        page_url = "https://btcapitalpartners.ro/taxe-si-comisioane"
        pdf_url = "https://btcapitalpartners.ro/storage/app/media/BTCP-Anexa-Taxe-si-comisioane.pdf"
        page_text = self._ascii_fold(self._strip_html(await self._fetch_text(page_url)))
        pdf_text = self._ascii_fold(re.sub(r"\s+", " ", await self._fetch_pdf_text(pdf_url)))

        bvb_small_match = re.search(r"<\s*100\.000\s*ron\s+([\d\.,]+)%", page_text, re.IGNORECASE)
        bvb_large_match = re.search(r">\s*1\.000\.000\s*ron\s+([\d\.,]+)%", page_text, re.IGNORECASE)
        ext_match = re.search(r"2\.\s*externe.*?comision de\s+([\d\.,]+)\s*%\s+din valoarea tranzactiilor", pdf_text, re.IGNORECASE)
        fx_match = re.search(r"marj\s*a\s+de\s+([\d\.,]+)%\s*,\s*pentru fiecare conversie", pdf_text, re.IGNORECASE)
        us_custody_match = re.search(r"sua\s+([\d\.,]+)%\s+5\s+usd", pdf_text, re.IGNORECASE)
        xetra_custody_match = re.search(r"germania:\s*xetra\s+([\d\.,]+)%\s+5\s+eur", pdf_text, re.IGNORECASE)
        high_custody_match = re.search(r"bulgaria6\s+([\d\.,]+)%\s+15", pdf_text, re.IGNORECASE)
        if not (
            bvb_small_match
            and bvb_large_match
            and ext_match
            and fx_match
            and us_custody_match
            and xetra_custody_match
            and high_custody_match
        ):
            raise ValueError("Nu am putut extrage costurile curente BT Capital Partners.")

        bvb_small = self._parse_percent(bvb_small_match.group(1))
        bvb_large = self._parse_percent(bvb_large_match.group(1))
        ext_fee = self._parse_percent(ext_match.group(1))
        fx_fee = self._parse_percent(fx_match.group(1))
        custody_low = min(
            self._parse_percent(us_custody_match.group(1)),
            self._parse_percent(xetra_custody_match.group(1)),
        )
        custody_high = self._parse_percent(high_custody_match.group(1))
        return self._build_offer(
            category="broker",
            provider="BT Capital Partners",
            product_name="BT Trade BVB + piete internationale",
            suitability="potrivit pentru investitori care vor ecosistem BT si acces atat la BVB, cat si la pietele externe importante",
            source_url=pdf_url,
            source_name="BT Capital Partners",
            currency="EUR",
            transaction_cost_percent=ext_fee,
            fx_conversion_cost_percent=fx_fee,
            custody_fee_percent=custody_low,
            cost_summary=(
                f"BVB online: intre {bvb_small:.2f}% si {bvb_large:.2f}% in functie de rulajul pe 3 luni. "
                f"Piete externe: {ext_fee:.2f}% pe tranzactie, la care se adauga costuri ale tertilor; custodia variaza orientativ intre {custody_low:.2f}% si {custody_high:.4f}% pe an, in functie de piata."
            ),
            note=(
                f"Pentru conversii valutare, anexa BT Capital Partners mentioneaza marja de {fx_fee:.2f}% pentru fiecare conversie fata de cursul de referinta folosit. "
                "Costurile de custodie si decontare pentru pietele externe pot include taxe suplimentare ale infrastructurii locale si TVA unde se aplica."
            ),
        )

    async def _build_bt_obligatiuni_offer(self) -> MarketOfferResponse:
        url = "https://www.btassetmanagement.ro/bt-obligatiuni"
        text = self._ascii_fold(self._strip_html(await self._fetch_text(url)))
        price_match = re.search(r"2026-\d{2}-\d{2}\s+([\d\.,]+)\s+\(valoarea unitatii", text, re.IGNORECASE)
        buy_match = re.search(r"comision de cumparare\s+([\d\.,]+)%", text, re.IGNORECASE)
        sell_match = re.search(r"comision de rascumparare\s+([\d\.,]+)%", text, re.IGNORECASE)
        admin_match = re.search(
            r"comision curent administrare fond\*?\s+([\d\.,]+)%/luna din media activelor nete",
            text,
            re.IGNORECASE,
        )
        if not (price_match and buy_match and sell_match and admin_match):
            raise ValueError("Nu am putut extrage costurile curente pentru BT Obligatiuni.")

        monthly_admin_fee = self._parse_percent(admin_match.group(1))
        annual_cost = round(monthly_admin_fee * 12, 2)
        return self._build_offer(
            category="bond_fund",
            provider="BT Asset Management",
            product_name="BT Obligatiuni",
            suitability="potrivit pentru investitori conservatori sau moderati care vor expunere pe obligatiuni si depozite",
            source_url=url,
            source_name="BT Asset Management",
            indicative_price=round(self._parse_percent(price_match.group(1)), 3),
            term_months=36,
            currency="RON",
            annual_cost_percent=annual_cost,
            subscription_fee_percent=self._parse_percent(buy_match.group(1)),
            redemption_fee_percent=self._parse_percent(sell_match.group(1)),
            cost_summary="Comisionul curent de administrare este 0.05% pe luna, deja reflectat in valoarea unitatii de fond.",
            note="Fond de obligatiuni administrat activ; pagina oficiala arata si componenta portofoliului intre obligatiuni de stat, obligatiuni corporative si depozite.",
        )

    async def _build_ing_romania_ron_bond_offer(self) -> MarketOfferResponse:
        url = "https://ing.ro/dam/ingro/doc/202404_Costuri-fonduri-mutuale-GSAM.pdf"
        text = re.sub(r"\s+", " ", await self._fetch_pdf_text(url))
        match = re.search(
            r"Goldman Sachs Romania RON Bond Obligatiuni LU0345402175\s+([\d\.,]+)%\s+\d+\s+([\d\.,]+)%\s+\d+\s+([\d\.,]+)%\s+\d+(?:[\.,]\d+)?\s+([\d\.,]+)%\s+\d+\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)",
            text,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Nu am putut extrage costurile curente pentru Goldman Sachs Romania RON Bond.")

        total_annual_cost = self._parse_percent(match.group(1))
        transaction_cost = self._parse_percent(match.group(3))
        subscription_fee = self._parse_percent(match.group(5))
        redemption_fee = self._parse_percent(match.group(6))
        custody_fee = self._parse_percent(match.group(7))
        return self._build_offer(
            category="bond_fund",
            provider="ING / Goldman Sachs Asset Management",
            product_name="Goldman Sachs Romania RON Bond",
            suitability="potrivit pentru investitori care vor obligatiuni in lei prin fond mutual distribuit de ING",
            source_url=url,
            source_name="ING / Goldman Sachs Asset Management",
            term_months=36,
            currency="RON",
            annual_cost_percent=total_annual_cost,
            transaction_cost_percent=transaction_cost,
            subscription_fee_percent=subscription_fee,
            redemption_fee_percent=redemption_fee,
            custody_fee_percent=custody_fee,
            cost_summary="Costul anual total include administrarea fondului, costurile de tranzactionare si alte cheltuieli deja deduse din valoarea unitatii de fond.",
            note="Estimarea oficiala ING este actualizata la aprilie 2025 pentru o investitie de referinta de 1.000 RON pe 1 an.",
        )

    async def _build_raiffeisen_euro_obligatiuni_offer(self) -> MarketOfferResponse:
        page_url = "https://www.raiffeisenfonduri.ro/ro/investitii/raiffeisen-euro-obligatiuni.html"
        kid_url = (
            "https://www.raiffeisenfonduri.ro/content/dam/rbi/invest/eu/ro/documents/"
            "raiffeisen-euro-obligatiuni/20250117-document-cu-informatii-esentiale-raiffeisen-euro-obligatiuni.pdf"
        )
        page_text = self._ascii_fold(self._strip_html(await self._fetch_text(page_url)))
        kid_text = self._ascii_fold(re.sub(r"\s+", " ", await self._fetch_pdf_text(kid_url)))

        sub_match = re.search(r"comision subscriere\s+([\d\.,]+)%", page_text, re.IGNORECASE)
        red_match = re.search(r"comision rascumparare\s+([\d\.,]+)%", page_text, re.IGNORECASE)
        order_match = re.search(r"comision preluare ordine\*?\s*([\d\.,]+)\s*%", page_text, re.IGNORECASE)
        annual_match = re.search(r"impactul anual al costurilor \(\*\)\s+([\d\.,]+)%", kid_text, re.IGNORECASE)
        admin_match = re.search(
            r"comisioane de administrare .*? ([\d\.,]+)% pe an din valoarea investitiei",
            kid_text,
            re.IGNORECASE,
        )
        transaction_match = re.search(
            r"costuri de tranzactionare\s+([\d\.,]+)%\s*(?:pe\s*)?an",
            kid_text,
            re.IGNORECASE,
        )
        if not (sub_match and red_match and order_match and annual_match and admin_match and transaction_match):
            raise ValueError("Nu am putut extrage costurile curente pentru Raiffeisen Euro Obligatiuni.")

        return self._build_offer(
            category="bond_fund",
            provider="Raiffeisen Asset Management",
            product_name="Raiffeisen Euro Obligatiuni",
            suitability="potrivit pentru investitori moderati care vor expunere pe obligatiuni denominate in euro",
            source_url=kid_url,
            source_name="Raiffeisen Asset Management",
            term_months=36,
            currency="EUR",
            annual_cost_percent=self._parse_percent(annual_match.group(1)),
            transaction_cost_percent=self._parse_percent(transaction_match.group(1)),
            subscription_fee_percent=self._parse_percent(sub_match.group(1)),
            redemption_fee_percent=self._parse_percent(red_match.group(1)),
            cost_summary=(
                f"Comisionul curent de preluare ordine este {self._parse_percent(order_match.group(1)):.2f}% in prezent si poate varia pana la maximum 0.35%, conform paginii oficiale."
            ),
            note="Documentul cu informatii esentiale arata costurile anuale curente, iar pagina fondului afiseaza separat comisioanele de subscriere si rascumparare.",
        )

    async def get_investment_options(self, target_months: int, risk_profile: str) -> list[MarketOfferResponse]:
        if target_months < 12:
            return []

        instruments: list[QuoteInstrument] = []
        manual_builders = []
        if target_months >= 12:
            instruments.append(
                QuoteInstrument(
                    symbol="VAGF.DE",
                    name="Vanguard Global Aggregate Bond UCITS ETF",
                    category="bond_fund",
                    suitability="potrivit ca varianta mai prudenta pentru obiective de peste 1 an",
                    currency="EUR",
                    source_url="https://fund-docs.vanguard.com/Global_Aggregate_Bond_UCITS_ETF_EUR_Hedged_Accumulating_9443_EU_INT_UK_EN.pdf",
                    source_name="Vanguard factsheet",
                    note="ETF de obligatiuni globale; mai potrivit pentru termen mediu decat actiunile pure.",
                    term_months=24,
                    annual_cost_percent=0.08,
                    cost_summary="Costul anual curent (OCF) nu include comisioanele brokerului si spread-ul de tranzactionare din piata secundara.",
                )
            )
        if target_months >= 36:
            manual_builders.extend(
                [
                    self._build_bt_obligatiuni_offer(),
                    self._build_ing_romania_ron_bond_offer(),
                    self._build_raiffeisen_euro_obligatiuni_offer(),
                ]
            )
            instruments.append(
                QuoteInstrument(
                    symbol="EUNL.DE",
                    name="iShares Core MSCI World UCITS ETF",
                    category="equity_fund",
                    suitability="potrivit pentru obiective pe termen lung si diversificare globala",
                    currency="EUR",
                    source_url="https://www.ishares.com/de/professionelle-anleger/de/produkte/251882/ishares-msci-world-ucits-etf-acc-fund?siteEntryPassthrough=true&switchLocale=y",
                    source_name="iShares / BlackRock",
                    note="ETF global axat pe actiuni dezvoltate; volatil pe termen scurt, mai potrivit pentru orizont lung.",
                    term_months=60,
                    annual_cost_percent=0.20,
                    cost_summary="TER-ul fondului nu include comisioanele brokerului, costul valutar sau spread-ul din piata secundara.",
                )
            )
        if target_months >= 60 and risk_profile == "aggressive":
            instruments.extend(
                [
                    QuoteInstrument(
                        symbol="SXR8.DE",
                        name="iShares Core S&P 500 UCITS ETF",
                        category="equity_fund",
                        suitability="potrivit pentru profil agresiv si orizont lung",
                        currency="EUR",
                        source_url="https://www.ishares.com/de/professionelle-anleger/de/produkte/253743/",
                        source_name="iShares / BlackRock",
                        note="Expunere pe companiile mari din SUA; util ca motor de crestere pe termen lung, nu pentru obiective apropiate.",
                        term_months=60,
                        annual_cost_percent=0.07,
                        cost_summary="TER-ul oficial nu include comisionul brokerului sau spread-ul de tranzactionare.",
                    ),
                    QuoteInstrument(
                        symbol="AAPL.US",
                        name="Apple Inc.",
                        category="stock",
                        suitability="potrivita doar pentru o componenta mica, mai agresiva, dintr-un obiectiv lung",
                        currency="USD",
                        source_url="https://www.apple.com/investor/",
                        source_name="Apple Investor Relations",
                        note="Actiune individuala mare si lichida; mai volatila decat un ETF diversificat.",
                        term_months=60,
                        cost_summary="Actiunea nu are comision de administrare propriu; costurile reale depind de broker, spread si eventualul schimb valutar.",
                    ),
                    QuoteInstrument(
                        symbol="MSFT.US",
                        name="Microsoft Corp.",
                        category="stock",
                        suitability="potrivita pentru profil agresiv si termen lung, doar ca pondere limitata",
                        currency="USD",
                        source_url="https://www.microsoft.com/en-us/investor",
                        source_name="Microsoft Investor Relations",
                        note="Actiune individuala din tehnologie cu lichiditate ridicata.",
                        term_months=60,
                        cost_summary="Actiunea nu are comision de administrare propriu; costurile reale depind de broker, spread si eventualul schimb valutar.",
                    ),
                ]
            )

        raw_results = await asyncio.gather(
            *manual_builders,
            *(self._build_quote_offer(instrument) for instrument in instruments),
            return_exceptions=True,
        )

        offers = [offer for offer in raw_results if isinstance(offer, MarketOfferResponse)]
        category_order = {"bond_fund": 0, "equity_fund": 1, "stock": 2}
        offers.sort(
            key=lambda item: (
                category_order.get(item.category, 9),
                item.annual_cost_percent if item.annual_cost_percent is not None else 999.0,
                -(item.indicative_price or 0.0),
            )
        )
        return offers

    async def _build_quote_offer(self, instrument: QuoteInstrument) -> MarketOfferResponse | None:
        url = f"https://stooq.com/q/l/?s={instrument.symbol.lower()}&i=d"
        async with httpx.AsyncClient(timeout=20.0, headers=self._headers) as client:
            response = await client.get(url)
            response.raise_for_status()

        parts = response.text.strip().split(",")
        if len(parts) < 7 or parts[1] == "N/D":
            return None

        last_price = float(parts[6])
        quote_date = parts[1]
        quote_dt = datetime.strptime(quote_date, "%Y%m%d").replace(tzinfo=timezone.utc)
        return self._build_offer(
            category=instrument.category,
            provider="Piata listata / cotatie indicativa",
            product_name=instrument.name,
            suitability=instrument.suitability,
            source_url=instrument.source_url,
            source_name=instrument.source_name,
            indicative_price=round(last_price, 3),
            term_months=instrument.term_months,
            currency=instrument.currency,
            annual_cost_percent=instrument.annual_cost_percent,
            transaction_cost_percent=instrument.transaction_cost_percent,
            subscription_fee_percent=instrument.subscription_fee_percent,
            redemption_fee_percent=instrument.redemption_fee_percent,
            custody_fee_percent=instrument.custody_fee_percent,
            cost_summary=instrument.cost_summary,
            note=instrument.note,
            retrieved_at=quote_dt,
        )
