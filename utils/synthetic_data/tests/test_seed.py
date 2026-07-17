from __future__ import annotations

from utils.synthetic_data.core.seed import SeedFactory


def test_same_context_produces_the_same_random_sequence() -> None:
    seed_factory = SeedFactory(42017)

    first = [
        seed_factory.rng("country", "0", "metrics").randint(0, 100)
        for _ in range(3)
    ]
    second = [
        seed_factory.rng("country", "0", "metrics").randint(0, 100)
        for _ in range(3)
    ]

    assert first == second


def test_contexts_have_independent_random_sequences() -> None:
    seed_factory = SeedFactory(42017)

    country_metric = seed_factory.rng("country", "0", "metrics").getstate()
    document_recipe = seed_factory.rng("document", "0", "recipe").getstate()

    assert country_metric != document_recipe
