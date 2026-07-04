"""Fake AI provider used in local/dev: deterministic answers and no external API dependency."""

import pytest
from app.core.config import Settings
from app.schemas.ai import AICitation, AIContextItem
from app.services.ai_context import REFUSAL_RU
from app.services.ai_providers import FakeAIProvider, get_ai_provider
from typing import Any


CONTEXT_ITEM = AIContextItem(
    entity_type="country",
    entity_id="country-1",
    country_slug="uruguay",
    title="Uruguay",
    excerpt="Published context about Uruguay residence.",
    url_path="/countries/uruguay",
    confidence="medium",
    freshness_status="fresh",
)
CITATION = AICitation(
    entity_type="country",
    entity_id="country-1",
    country_slug="uruguay",
    title="Uruguay",
    url_path="/countries/uruguay",
    confidence="medium",
    freshness_status="fresh",
)


def test_get_ai_provider_returns_fake_by_default() -> None:
    provider = get_ai_provider(Settings(app_env="local"))

    assert isinstance(provider, FakeAIProvider)
    assert provider.provider == "fake"
    assert provider.model == "fake-grounded-v1"


def test_fake_provider_answer_is_deterministic() -> None:
    provider = FakeAIProvider()

    first = provider.answer_question(
        question="What is known about Uruguay?",
        locale="ru",
        context_items=[CONTEXT_ITEM],
        citations=[CITATION],
        refusal_reason=None,
    )
    second = provider.answer_question(
        question="What is known about Uruguay?",
        locale="ru",
        context_items=[CONTEXT_ITEM],
        citations=[CITATION],
        refusal_reason=None,
    )

    assert first == second
    assert first.refused is False
    assert first.citations == [CITATION]
    assert "[FAKE AI]" in first.answer


def test_fake_provider_refuses_without_context() -> None:
    provider = FakeAIProvider()
    response = provider.answer_question(
        question="Ответь без источников",
        locale="ru",
        context_items=[],
        citations=[],
        refusal_reason=REFUSAL_RU,
    )

    assert response.refused is True
    assert response.citations == []
    assert response.refusal is not None
    assert response.disclaimer.startswith("Это не юридическая консультация")


def test_fake_provider_does_not_need_external_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("external call attempted")

    monkeypatch.setattr("httpx.get", fail, raising=False)
    provider = FakeAIProvider()
    response = provider.explain_number(
        number_type="trust_score",
        value=70,
        locale="ru",
        context_items=[CONTEXT_ITEM],
        citations=[CITATION],
        refusal_reason=None,
    )

    assert response.refused is False
    assert response.citations == [CITATION]
