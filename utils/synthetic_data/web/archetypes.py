from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from utils.synthetic_data.core.paths import DEFAULT_INPUT_DATA_DIR


DEFAULT_WEB_CONFIG_FILE = DEFAULT_INPUT_DATA_DIR / "web_config.json"

_KNOWN_PAGE_KINDS = frozenset({"source", "article", "notice"})
_KNOWN_ANOMALY_KINDS = frozenset(
    {
        "not_found",
        "server_error",
        "redirect",
        "duplicate",
        "empty",
        "huge",
        "broken_encoding",
    }
)


class WebConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class SiteArchetype:
    slug: str
    label: str
    title_template: str
    page_kinds: tuple[str, ...]

    def title_for(self, country_name: str) -> str:
        return self.title_template.format(country=country_name)


@dataclass(frozen=True)
class WebConfig:
    schema_version: str
    site_archetypes: tuple[SiteArchetype, ...]
    cross_site_links_min: int
    cross_site_links_max: int
    anomaly_ratios: dict[str, float]
    huge_page_padding_paragraphs: int

    def archetype_by_slug(self, slug: str) -> SiteArchetype:
        for archetype in self.site_archetypes:
            if archetype.slug == slug:
                return archetype
        raise WebConfigError(f"Unknown site archetype: {slug}")


def _mapping(value: object, *, field: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WebConfigError(f"{path}: {field} must be an object")
    return value


def _string(value: object, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WebConfigError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def _positive_int(value: object, *, field: str, path: Path) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise WebConfigError(f"{path}: {field} must be a non-negative integer")
    return value


def _ratio(value: object, *, field: str, path: Path) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise WebConfigError(f"{path}: {field} must be a number")
    if not 0.0 <= float(value) <= 1.0:
        raise WebConfigError(f"{path}: {field} must be between 0.0 and 1.0")
    return float(value)


def _load_site_archetypes(
    value: object, *, path: Path
) -> tuple[SiteArchetype, ...]:
    if not isinstance(value, list) or not value:
        raise WebConfigError(
            f"{path}: site_archetypes must be a non-empty list"
        )

    archetypes: list[SiteArchetype] = []
    for index, raw in enumerate(value):
        payload = _mapping(raw, field=f"site_archetypes[{index}]", path=path)
        page_kinds_raw = payload.get("page_kinds")
        if not isinstance(page_kinds_raw, list) or not page_kinds_raw:
            raise WebConfigError(
                f"{path}: site_archetypes[{index}].page_kinds must be a "
                "non-empty list"
            )
        page_kinds = tuple(
            _string(item, field="page_kinds[]", path=path)
            for item in page_kinds_raw
        )
        unknown_kinds = set(page_kinds) - _KNOWN_PAGE_KINDS
        if unknown_kinds:
            raise WebConfigError(
                f"{path}: site_archetypes[{index}].page_kinds has unknown "
                f"kinds {sorted(unknown_kinds)}; expected a subset of "
                f"{sorted(_KNOWN_PAGE_KINDS)}"
            )
        title_template = _string(
            payload.get("title_template"), field="title_template", path=path
        )
        if "{country}" not in title_template:
            raise WebConfigError(
                f"{path}: site_archetypes[{index}].title_template must "
                "contain a {country} placeholder"
            )
        archetypes.append(
            SiteArchetype(
                slug=_string(payload.get("slug"), field="slug", path=path),
                label=_string(payload.get("label"), field="label", path=path),
                title_template=title_template,
                page_kinds=page_kinds,
            )
        )
    if len({archetype.slug for archetype in archetypes}) != len(archetypes):
        raise WebConfigError(f"{path}: site archetype slugs must be unique")
    return tuple(archetypes)


def _load_anomaly_ratios(value: object, *, path: Path) -> dict[str, float]:
    payload = _mapping(value, field="anomaly_ratios", path=path)
    if set(payload) != _KNOWN_ANOMALY_KINDS:
        missing = sorted(_KNOWN_ANOMALY_KINDS - set(payload))
        unexpected = sorted(set(payload) - _KNOWN_ANOMALY_KINDS)
        raise WebConfigError(
            f"{path}: anomaly_ratios must define exactly the known "
            f"anomaly kinds; missing={missing}, unexpected={unexpected}"
        )
    return {
        kind: _ratio(payload[kind], field=f"anomaly_ratios.{kind}", path=path)
        for kind in _KNOWN_ANOMALY_KINDS
    }


def load_web_config(path: Path = DEFAULT_WEB_CONFIG_FILE) -> WebConfig:
    if not path.exists():
        raise WebConfigError(f"Web config file not found: {path}")
    try:
        payload: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise WebConfigError(f"{path}: invalid JSON ({error})") from error

    root = _mapping(payload, field="root", path=path)
    cross_site_links = _mapping(
        root.get("cross_site_links"), field="cross_site_links", path=path
    )
    minimum = _positive_int(
        cross_site_links.get("minimum"),
        field="cross_site_links.minimum",
        path=path,
    )
    maximum = _positive_int(
        cross_site_links.get("maximum"),
        field="cross_site_links.maximum",
        path=path,
    )
    if minimum > maximum:
        raise WebConfigError(
            f"{path}: cross_site_links.minimum must not exceed maximum"
        )

    return WebConfig(
        schema_version=_string(
            root.get("schema_version"), field="schema_version", path=path
        ),
        site_archetypes=_load_site_archetypes(
            root.get("site_archetypes"), path=path
        ),
        cross_site_links_min=minimum,
        cross_site_links_max=maximum,
        anomaly_ratios=_load_anomaly_ratios(
            root.get("anomaly_ratios"), path=path
        ),
        huge_page_padding_paragraphs=_positive_int(
            root.get("huge_page_padding_paragraphs"),
            field="huge_page_padding_paragraphs",
            path=path,
        ),
    )
