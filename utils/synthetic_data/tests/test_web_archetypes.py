from __future__ import annotations

import json
import pytest
from pathlib import Path
from utils.synthetic_data.web.archetypes import WebConfigError, load_web_config


def _base_config() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "site_archetypes": [
            {
                "slug": "gov_portal",
                "label": "Government portal",
                "title_template": "{country} Government Portal",
                "page_kinds": ["source"],
            }
        ],
        "cross_site_links": {"minimum": 1, "maximum": 2},
        "anomaly_ratios": {
            "not_found": 0.1,
            "server_error": 0.1,
            "redirect": 0.1,
            "duplicate": 0.1,
            "empty": 0.1,
            "huge": 0.1,
            "broken_encoding": 0.1,
        },
        "huge_page_padding_paragraphs": 10,
    }


def _write(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "web_config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_default_web_config_loads_successfully() -> None:
    config = load_web_config()

    assert config.site_archetypes
    assert set(config.anomaly_ratios) == {
        "not_found",
        "server_error",
        "redirect",
        "duplicate",
        "empty",
        "huge",
        "broken_encoding",
    }
    assert config.cross_site_links_min <= config.cross_site_links_max


def test_missing_file_raises_web_config_error(tmp_path: Path) -> None:
    with pytest.raises(WebConfigError, match="not found"):
        load_web_config(tmp_path / "does-not-exist.json")


def test_unknown_page_kind_is_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    payload["site_archetypes"][0]["page_kinds"] = ["not-a-real-kind"]  # type: ignore[index]

    with pytest.raises(WebConfigError, match="unknown kinds"):
        load_web_config(_write(tmp_path, payload))


def test_title_template_without_placeholder_is_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    payload["site_archetypes"][0]["title_template"] = "Static Title"  # type: ignore[index]

    with pytest.raises(WebConfigError, match="placeholder"):
        load_web_config(_write(tmp_path, payload))


def test_duplicate_archetype_slugs_are_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    payload["site_archetypes"] = payload["site_archetypes"] * 2  # type: ignore[operator]

    with pytest.raises(WebConfigError, match="unique"):
        load_web_config(_write(tmp_path, payload))


def test_missing_anomaly_kind_is_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    anomaly_ratios = payload["anomaly_ratios"]
    assert isinstance(anomaly_ratios, dict)
    del anomaly_ratios["not_found"]

    with pytest.raises(WebConfigError, match="anomaly_ratios"):
        load_web_config(_write(tmp_path, payload))


def test_anomaly_ratio_out_of_range_is_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    payload["anomaly_ratios"]["not_found"] = 1.5  # type: ignore[index]

    with pytest.raises(WebConfigError, match="between 0\\.0 and 1\\.0"):
        load_web_config(_write(tmp_path, payload))


def test_cross_site_links_min_over_max_is_rejected(tmp_path: Path) -> None:
    payload = _base_config()
    payload["cross_site_links"] = {"minimum": 5, "maximum": 1}

    with pytest.raises(WebConfigError, match="must not exceed"):
        load_web_config(_write(tmp_path, payload))


def test_invalid_json_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "web_config.json"
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(WebConfigError, match="invalid JSON"):
        load_web_config(path)
