import re


PII_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"(?:\+?\d[\s().-]*){8,}"),
    re.compile(r"(?<!\w)@[A-Za-z0-9_]{4,32}\b"),
    re.compile(r"https?://|www\.", re.IGNORECASE),
)


def contains_pii(*texts: str) -> bool:
    combined = "\n".join(texts)
    return any(pattern.search(combined) for pattern in PII_PATTERNS)
