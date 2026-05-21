def normalize_locale(raw_locale: str | None) -> str:
    if not raw_locale:
        return "ro"

    lowered = raw_locale.lower()
    if lowered.startswith("en"):
        return "en"
    return "ro"


def is_english(locale: str | None) -> bool:
    return normalize_locale(locale) == "en"
