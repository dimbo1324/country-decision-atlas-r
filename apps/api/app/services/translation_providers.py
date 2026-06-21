from __future__ import annotations

from pydantic import BaseModel
import time
from typing import Any


class TranslationInput(BaseModel):
    source_text: str
    source_locale: str
    target_locale: str
    entity_type: str | None = None
    field_name: str | None = None
    domain: str = "legal_migration"
    glossary_terms: dict[str, str] | None = None
    preserve_terms: list[str] | None = None


class TranslationResult(BaseModel):
    text: str
    provider: str
    provider_model: str
    quality_score: float | None = None
    input_chars: int | None = None
    output_chars: int | None = None
    duration_ms: int | None = None
    raw_metadata: dict[str, Any] | None = None


class TranslationProvider:
    def translate(self, input: TranslationInput) -> TranslationResult:
        raise NotImplementedError


class FakeTranslationProvider(TranslationProvider):
    PROVIDER = "fake"
    PROVIDER_MODEL = "fake-v1"

    def translate(self, input: TranslationInput) -> TranslationResult:
        return TranslationResult(
            text=f"[FAKE {input.target_locale}] {input.source_text}",
            provider=self.PROVIDER,
            provider_model=self.PROVIDER_MODEL,
            input_chars=len(input.source_text),
            output_chars=len(input.source_text) + 12,
            duration_ms=1,
        )


_MIGRATION_GLOSSARY: dict[str, str] = {
    "ВНЖ": "residence permit",
    "ПМЖ": "permanent residence",
    "гражданство": "citizenship",
    "налоговый резидент": "tax resident",
    "источник": "source",
    "доказательство": "evidence",
    "виза": "visa",
    "разрешение на работу": "work permit",
    "регистрация": "registration",
    "страховой номер": "social security number",
}


def _build_system_prompt(input: TranslationInput) -> str:
    glossary_lines = ""
    if input.glossary_terms:
        terms = {**_MIGRATION_GLOSSARY, **input.glossary_terms}
    else:
        terms = _MIGRATION_GLOSSARY
    glossary_lines = "\n".join(f"- {k} → {v}" for k, v in terms.items())

    preserve_block = ""
    if input.preserve_terms:
        preserve_block = "Preserve exactly without translation:\n" + "\n".join(
            f"- {t}" for t in input.preserve_terms
        )

    return f"""You are a professional legal and immigration document translator.

Task: Translate the user text from {input.source_locale} to {input.target_locale}.

Rules:
- Translate only the text, nothing else
- Preserve all numbers, dates, percentages exactly
- Preserve names of laws, articles, regulations exactly
- Preserve organization names exactly
- Preserve URLs and source names exactly
- Do not add new facts or information
- Do not explain the translation
- Do not add disclaimers
- Do not shorten or expand the meaning
- Do not interpret legal provisions
- Do not provide legal advice
- Return only the translated text, no preamble

Domain: {input.domain}

Terminology glossary (use these translations for these terms):
{glossary_lines}

{preserve_block}"""


class AITranslationProvider(TranslationProvider):
    PROVIDER = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        timeout_seconds: int = 30,
        max_retries: int = 2,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_seconds
        self._max_retries = max_retries

    def translate(self, input: TranslationInput) -> TranslationResult:
        import httpx

        system_prompt = _build_system_prompt(input)
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input.source_text},
            ],
            "temperature": 0.1,
            "max_tokens": min(4096, max(256, len(input.source_text) * 3)),
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                t0 = time.monotonic()
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.post(
                        "https://api.openai.com/v1/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                duration_ms = int((time.monotonic() - t0) * 1000)
                resp.raise_for_status()
                data = resp.json()
                translated = data["choices"][0]["message"]["content"].strip()
                usage = data.get("usage", {})
                return TranslationResult(
                    text=translated,
                    provider=self.PROVIDER,
                    provider_model=self._model,
                    input_chars=len(input.source_text),
                    output_chars=len(translated),
                    duration_ms=duration_ms,
                    raw_metadata={
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "request_id": resp.headers.get("x-request-id"),
                        "attempt": attempt + 1,
                    },
                )
            except Exception as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    time.sleep(1.0 * (attempt + 1))
        raise RuntimeError(
            f"AI translation failed after {self._max_retries + 1} attempts: {last_exc}"
        )


def get_translation_provider() -> TranslationProvider:
    from app.core.config import get_settings

    settings = get_settings()
    provider_name = settings.translation_provider.lower()

    if provider_name == "ai":
        sub = settings.ai_translation_provider.lower()
        if sub == "openai":
            api_key = settings.ai_translation_api_key
            if not api_key:
                raise RuntimeError(
                    "AI_TRANSLATION_API_KEY is required when TRANSLATION_PROVIDER=ai"
                )
            return AITranslationProvider(
                api_key=api_key,
                model=settings.ai_translation_model,
                timeout_seconds=settings.ai_translation_timeout_seconds,
                max_retries=settings.ai_translation_max_retries,
            )
        raise RuntimeError(f"Unknown AI translation sub-provider: {sub}")

    return FakeTranslationProvider()
