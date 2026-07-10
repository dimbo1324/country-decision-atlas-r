from __future__ import annotations

from scripts.synthetic_data.core.seed import SeedFactory
from scripts.synthetic_data.core.world_input import REQUIRED_METRICS, WorldInput
from scripts.synthetic_data.core.world_models import (
    SyntheticArticle,
    SyntheticAuthor,
    SyntheticComment,
    SyntheticCountry,
    SyntheticLegalSignal,
    SyntheticUser,
)
from typing import NamedTuple


EMAIL_DOMAIN = "example.test"
_LOCALE = "en-US"
_MODERATION_STATUSES = ("approved", "pending", "hidden")
_COMMENT_TEMPLATES = (
    "This matches what I've read about {name} recently.",
    "Not sure this fully reflects the current situation in {name}.",
    "Good summary of {name}'s trend this period.",
)


class CountryContent(NamedTuple):
    users: tuple[SyntheticUser, ...]
    author: SyntheticAuthor
    article: SyntheticArticle
    comments: tuple[SyntheticComment, ...]
    legal_signal: SyntheticLegalSignal


def _humanize(metric: str) -> str:
    return metric.replace("_", " ")


def _generate_user(
    *,
    seed_factory: SeedFactory,
    world_input: WorldInput,
    role: str,
    slug: str,
) -> SyntheticUser:
    rng = seed_factory.rng("user", slug)
    given = rng.choice(world_input.user_given_names)
    family = rng.choice(world_input.user_family_names)
    return SyntheticUser(
        user_id=f"user-{slug}",
        display_name=f"{given} {family}",
        email=f"{slug}@{EMAIL_DOMAIN}",
        role=role,
        locale=_LOCALE,
    )


def generate_country_content(
    *,
    country: SyntheticCountry,
    world_input: WorldInput,
    seed_factory: SeedFactory,
) -> CountryContent:
    """Generate the author, article, comments, and legal signal for one
    country, all tied to its existing Stage-2 event and source so that a
    recent legal signal is always reflected in the metric history and
    related materials (spec section 7.2)."""
    rng = seed_factory.rng("content", country.slug)

    author_user = _generate_user(
        seed_factory=seed_factory,
        world_input=world_input,
        role="author",
        slug=f"{country.slug}-author",
    )
    commenter_users = tuple(
        _generate_user(
            seed_factory=seed_factory,
            world_input=world_input,
            role="user",
            slug=f"{country.slug}-commenter-{index}",
        )
        for index in range(2)
    )
    users = (author_user, *commenter_users)

    author = SyntheticAuthor(
        author_id=f"author-{country.slug}",
        user_id=author_user.user_id,
        display_name=author_user.display_name,
        reputation=rng.randint(20, 95),
        specialization=rng.choice(REQUIRED_METRICS),
        bio=f"Synthetic author focused on {country.name} coverage.",
    )

    event = country.events[0]
    source = country.sources[0]

    article = SyntheticArticle(
        article_id=f"article-{country.slug}",
        author_id=author.author_id,
        country_id=country.country_id,
        title=f"{country.name}: what changed and why it matters",
        summary=(
            f"A synthetic overview of {country.name}, covering its "
            f"{_humanize(event.metric)} trend and supporting sources."
        ),
        source_ids=(source.source_id,),
        published_as_of=event.as_of,
    )

    comments = tuple(
        SyntheticComment(
            comment_id=f"comment-{country.slug}-{index}",
            article_id=article.article_id,
            user_id=commenter_users[index % len(commenter_users)].user_id,
            body=rng.choice(_COMMENT_TEMPLATES).format(name=country.name),
            created_as_of=event.as_of,
            moderation_status=_MODERATION_STATUSES[
                index % len(_MODERATION_STATUSES)
            ],
        )
        for index in range(3)
    )

    legal_signal = SyntheticLegalSignal(
        signal_id=f"legal-{country.slug}",
        country_id=country.country_id,
        event_id=event.event_id,
        affected_country_ids=(country.country_id,),
        effective_as_of=event.as_of,
        impact="positive" if event.direction == "improved" else "negative",
        confidence=source.confidence,
        source_id=source.source_id,
    )

    return CountryContent(
        users=users,
        author=author,
        article=article,
        comments=comments,
        legal_signal=legal_signal,
    )
