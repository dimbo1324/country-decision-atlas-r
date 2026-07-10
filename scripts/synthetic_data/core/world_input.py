from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from scripts.synthetic_data.core.paths import DEFAULT_WORLD_INPUT_FILE
from typing import Any


REQUIRED_METRICS = (
    "economy",
    "cost_of_living",
    "safety",
    "civil_freedoms",
    "institutional_stability",
    "digital_infrastructure",
    "migration_openness",
    "data_confidence",
)

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL_PATTERN = re.compile(r"\b\w+://")
_SECRET_KEYWORD_PATTERN = re.compile(
    r"(password|secret|api[_-]?key|private[_-]?key|access[_-]?token|"
    r"auth[_-]?token|bearer\s)",
    re.IGNORECASE,
)
_ALLOWED_URL_SCHEME_PREFIXES = ("synthetic://",)


class WorldInputError(RuntimeError):
    pass


def _ensure_input_is_safe(value: object, *, path: Path, context: str) -> None:
    """Reject production settings, PII-like values, and unexpected network
    addresses anywhere in the raw input payload (spec section 23, stage 1,
    item 6)."""
    if isinstance(value, str):
        if _EMAIL_PATTERN.search(value):
            raise WorldInputError(
                f"{path}: {context} looks like a real e-mail address, "
                "which is not allowed in generator input"
            )
        if _URL_PATTERN.search(value) and not value.startswith(
            _ALLOWED_URL_SCHEME_PREFIXES
        ):
            raise WorldInputError(
                f"{path}: {context} contains a network address, which is "
                "not allowed in generator input"
            )
        if _SECRET_KEYWORD_PATTERN.search(value):
            raise WorldInputError(
                f"{path}: {context} looks like a secret or credential, "
                "which is not allowed in generator input"
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _ensure_input_is_safe(key, path=path, context=f"{context}.{key}")
            _ensure_input_is_safe(item, path=path, context=f"{context}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _ensure_input_is_safe(
                item, path=path, context=f"{context}[{index}]"
            )


@dataclass(frozen=True)
class MetricRange:
    minimum: int
    maximum: int


@dataclass(frozen=True)
class ArchetypeInput:
    slug: str
    label: str
    metric_ranges: dict[str, MetricRange]


@dataclass(frozen=True)
class ProfileInput:
    slug: str
    archetypes: tuple[str, ...]
    event_intensity: int


@dataclass(frozen=True)
class TextBlockInput:
    id: str
    kind: str
    applies_to: tuple[str, ...]
    requires: tuple[str, ...]
    variants: tuple[str, ...]


@dataclass(frozen=True)
class DocumentRecipeInput:
    id: str
    blocks: tuple[str, ...]


@dataclass(frozen=True)
class WorldInput:
    schema_version: str
    default_country_count: int
    name_prefixes: tuple[str, ...]
    name_suffixes: tuple[str, ...]
    forbidden_country_names: tuple[str, ...]
    archetypes: tuple[ArchetypeInput, ...]
    profiles: tuple[ProfileInput, ...]
    user_given_names: tuple[str, ...]
    user_family_names: tuple[str, ...]
    document_blocks: tuple[TextBlockInput, ...]
    document_recipes: tuple[DocumentRecipeInput, ...]
    source_checksum: str

    def archetype_by_slug(self, slug: str) -> ArchetypeInput:
        for archetype in self.archetypes:
            if archetype.slug == slug:
                return archetype
        raise WorldInputError(f"Unknown country archetype: {slug}")

    def profile_by_slug(self, slug: str) -> ProfileInput:
        for profile in self.profiles:
            if profile.slug == slug:
                return profile
        raise WorldInputError(f"Unknown world profile: {slug}")

    def document_block_by_id(self, block_id: str) -> TextBlockInput:
        for block in self.document_blocks:
            if block.id == block_id:
                return block
        raise WorldInputError(f"Unknown document block: {block_id}")

    def document_recipe_by_id(self, recipe_id: str) -> DocumentRecipeInput:
        for recipe in self.document_recipes:
            if recipe.id == recipe_id:
                return recipe
        raise WorldInputError(f"Unknown document recipe: {recipe_id}")


def _mapping(value: object, *, field: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WorldInputError(f"{path}: {field} must be an object")
    return value


def _string(value: object, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorldInputError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def _integer(
    value: object,
    *,
    field: str,
    path: Path,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise WorldInputError(f"{path}: {field} must be an integer")
    if not minimum <= value <= maximum:
        raise WorldInputError(
            f"{path}: {field} must be between {minimum} and {maximum}"
        )
    return value


def _string_list(
    value: object, *, field: str, path: Path, minimum_length: int = 1
) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) < minimum_length:
        raise WorldInputError(
            f"{path}: {field} must be a list with at least {minimum_length} items"
        )
    values = tuple(_string(item, field=field, path=path) for item in value)
    if len({item.casefold() for item in values}) != len(values):
        raise WorldInputError(f"{path}: {field} must not contain duplicates")
    return values


def _metric_ranges(
    value: object, *, field: str, path: Path
) -> dict[str, MetricRange]:
    payload = _mapping(value, field=field, path=path)
    if set(payload) != set(REQUIRED_METRICS):
        missing = sorted(set(REQUIRED_METRICS) - set(payload))
        unexpected = sorted(set(payload) - set(REQUIRED_METRICS))
        raise WorldInputError(
            f"{path}: {field} must define exactly the required metrics; "
            f"missing={missing}, unexpected={unexpected}"
        )

    ranges: dict[str, MetricRange] = {}
    for metric in REQUIRED_METRICS:
        range_payload = _mapping(
            payload[metric], field=f"{field}.{metric}", path=path
        )
        minimum = _integer(
            range_payload.get("minimum"),
            field=f"{field}.{metric}.minimum",
            path=path,
            minimum=0,
            maximum=100,
        )
        maximum = _integer(
            range_payload.get("maximum"),
            field=f"{field}.{metric}.maximum",
            path=path,
            minimum=0,
            maximum=100,
        )
        if minimum > maximum:
            raise WorldInputError(
                f"{path}: {field}.{metric}.minimum must not exceed maximum"
            )
        ranges[metric] = MetricRange(minimum=minimum, maximum=maximum)
    return ranges


def _load_archetypes(
    value: object, *, path: Path
) -> tuple[ArchetypeInput, ...]:
    if not isinstance(value, list) or len(value) < 5:
        raise WorldInputError(
            f"{path}: archetypes must contain at least 5 items"
        )

    archetypes: list[ArchetypeInput] = []
    for index, raw_archetype in enumerate(value):
        payload = _mapping(
            raw_archetype, field=f"archetypes[{index}]", path=path
        )
        archetypes.append(
            ArchetypeInput(
                slug=_string(
                    payload.get("slug"), field="archetype.slug", path=path
                ),
                label=_string(
                    payload.get("label"), field="archetype.label", path=path
                ),
                metric_ranges=_metric_ranges(
                    payload.get("metric_ranges"),
                    field="archetype.metric_ranges",
                    path=path,
                ),
            )
        )
    if len({archetype.slug for archetype in archetypes}) != len(archetypes):
        raise WorldInputError(f"{path}: archetype slugs must be unique")
    return tuple(archetypes)


def _load_profiles(
    value: object, *, path: Path, archetypes: tuple[ArchetypeInput, ...]
) -> tuple[ProfileInput, ...]:
    if not isinstance(value, list) or not value:
        raise WorldInputError(f"{path}: profiles must be a non-empty list")

    available_archetypes = {archetype.slug for archetype in archetypes}
    profiles: list[ProfileInput] = []
    for index, raw_profile in enumerate(value):
        payload = _mapping(raw_profile, field=f"profiles[{index}]", path=path)
        profile_archetypes = _string_list(
            payload.get("archetypes"),
            field="profile.archetypes",
            path=path,
            minimum_length=4,
        )
        unknown_archetypes = set(profile_archetypes) - available_archetypes
        if unknown_archetypes:
            raise WorldInputError(
                f"{path}: profile references unknown archetypes: "
                f"{sorted(unknown_archetypes)}"
            )
        profiles.append(
            ProfileInput(
                slug=_string(
                    payload.get("slug"), field="profile.slug", path=path
                ),
                archetypes=profile_archetypes,
                event_intensity=_integer(
                    payload.get("event_intensity"),
                    field="profile.event_intensity",
                    path=path,
                    minimum=1,
                    maximum=10,
                ),
            )
        )
    if len({profile.slug for profile in profiles}) != len(profiles):
        raise WorldInputError(f"{path}: profile slugs must be unique")
    return tuple(profiles)


def _load_document_blocks(
    value: object, *, path: Path
) -> tuple[TextBlockInput, ...]:
    if not isinstance(value, list) or not value:
        raise WorldInputError(
            f"{path}: document_blocks must be a non-empty list"
        )

    blocks: list[TextBlockInput] = []
    for index, raw_block in enumerate(value):
        payload = _mapping(
            raw_block, field=f"document_blocks[{index}]", path=path
        )
        blocks.append(
            TextBlockInput(
                id=_string(payload.get("id"), field="block.id", path=path),
                kind=_string(
                    payload.get("kind"), field="block.kind", path=path
                ),
                applies_to=_string_list(
                    payload.get("applies_to"),
                    field="block.applies_to",
                    path=path,
                ),
                requires=_string_list(
                    payload.get("requires"),
                    field="block.requires",
                    path=path,
                ),
                variants=_string_list(
                    payload.get("variants"),
                    field="block.variants",
                    path=path,
                ),
            )
        )
    if len({block.id for block in blocks}) != len(blocks):
        raise WorldInputError(f"{path}: document block ids must be unique")
    return tuple(blocks)


def _load_document_recipes(
    value: object, *, path: Path, blocks: tuple[TextBlockInput, ...]
) -> tuple[DocumentRecipeInput, ...]:
    if not isinstance(value, list) or not value:
        raise WorldInputError(
            f"{path}: document_recipes must be a non-empty list"
        )

    available_blocks = {block.id for block in blocks}
    recipes: list[DocumentRecipeInput] = []
    for index, raw_recipe in enumerate(value):
        payload = _mapping(
            raw_recipe, field=f"document_recipes[{index}]", path=path
        )
        recipe_blocks = _string_list(
            payload.get("blocks"), field="recipe.blocks", path=path
        )
        unknown_blocks = set(recipe_blocks) - available_blocks
        if unknown_blocks:
            raise WorldInputError(
                f"{path}: recipe references unknown blocks: "
                f"{sorted(unknown_blocks)}"
            )
        recipes.append(
            DocumentRecipeInput(
                id=_string(payload.get("id"), field="recipe.id", path=path),
                blocks=recipe_blocks,
            )
        )
    if len({recipe.id for recipe in recipes}) != len(recipes):
        raise WorldInputError(f"{path}: document recipe ids must be unique")
    return tuple(recipes)


def load_world_input(path: Path = DEFAULT_WORLD_INPUT_FILE) -> WorldInput:
    if not path.exists():
        raise WorldInputError(f"World input file not found: {path}")

    raw_bytes = path.read_bytes()
    try:
        payload: object = json.loads(raw_bytes.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise WorldInputError(f"{path}: input must be UTF-8") from error
    except json.JSONDecodeError as error:
        raise WorldInputError(f"{path}: invalid JSON ({error})") from error

    _ensure_input_is_safe(payload, path=path, context="root")

    root = _mapping(payload, field="root", path=path)
    archetypes = _load_archetypes(root.get("archetypes"), path=path)
    document_blocks = _load_document_blocks(
        root.get("document_blocks"), path=path
    )
    return WorldInput(
        schema_version=_string(
            root.get("schema_version"), field="schema_version", path=path
        ),
        default_country_count=_integer(
            root.get("default_country_count"),
            field="default_country_count",
            path=path,
            minimum=4,
            maximum=5,
        ),
        name_prefixes=_string_list(
            root.get("name_prefixes"),
            field="name_prefixes",
            path=path,
            minimum_length=5,
        ),
        name_suffixes=_string_list(
            root.get("name_suffixes"),
            field="name_suffixes",
            path=path,
            minimum_length=5,
        ),
        forbidden_country_names=_string_list(
            root.get("forbidden_country_names"),
            field="forbidden_country_names",
            path=path,
        ),
        archetypes=archetypes,
        profiles=_load_profiles(
            root.get("profiles"), path=path, archetypes=archetypes
        ),
        user_given_names=_string_list(
            root.get("user_given_names"),
            field="user_given_names",
            path=path,
            minimum_length=5,
        ),
        user_family_names=_string_list(
            root.get("user_family_names"),
            field="user_family_names",
            path=path,
            minimum_length=5,
        ),
        document_blocks=document_blocks,
        document_recipes=_load_document_recipes(
            root.get("document_recipes"),
            path=path,
            blocks=document_blocks,
        ),
        source_checksum=hashlib.sha256(raw_bytes).hexdigest(),
    )
