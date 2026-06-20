from pydantic import BaseModel


class TranslationMeta(BaseModel):
    requested_locale: str
    resolved_locale: str
    source_locale: str
    status: str
    method: str | None = None
    is_original: bool
    is_fallback: bool
    is_stale: bool = False
    quality_score: float | None = None


class LocalizedText(BaseModel):
    text: str
    meta: TranslationMeta
