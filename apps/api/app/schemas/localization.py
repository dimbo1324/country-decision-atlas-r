from pydantic import BaseModel, Field


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


class TranslationFieldMeta(BaseModel):
    field_name: str
    requested_locale: str
    resolved_locale: str
    source_locale: str
    status: str
    method: str | None = None
    is_original: bool
    is_fallback: bool
    is_stale: bool
    translation_unit_id: str | None = None
    translation_variant_id: str | None = None
    quality_score: float | None = None


class LocalizationMeta(BaseModel):
    requested_locale: str
    resolved_locale: str
    status: str
    is_fallback: bool
    has_machine_translation: bool
    has_human_review: bool
    has_stale_fields: bool
    missing_fields: list[str] = Field(default_factory=list)
    stale_fields: list[str] = Field(default_factory=list)
    fields: list[TranslationFieldMeta] = Field(default_factory=list)
