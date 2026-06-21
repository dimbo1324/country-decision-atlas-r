from pydantic import BaseModel


class TranslationResult(BaseModel):
    text: str
    provider: str
    provider_model: str


class TranslationProvider:
    def translate(
        self,
        source_text: str,
        source_locale: str,
        target_locale: str,
    ) -> TranslationResult:
        raise NotImplementedError


class FakeTranslationProvider(TranslationProvider):
    PROVIDER = "fake"
    PROVIDER_MODEL = "fake-v1"

    def translate(
        self,
        source_text: str,
        source_locale: str,  # noqa: ARG002
        target_locale: str,
    ) -> TranslationResult:
        return TranslationResult(
            text=f"[FAKE {target_locale}] {source_text}",
            provider=self.PROVIDER,
            provider_model=self.PROVIDER_MODEL,
        )
