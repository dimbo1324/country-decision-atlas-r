from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from scripts.synthetic_data.core.paths import DEFAULT_INPUT_DATA_DIR


DEFAULT_LOCALE_CORPUS_FILE = DEFAULT_INPUT_DATA_DIR / "locale_corpus.json"

REQUIRED_LOCALES: tuple[str, ...] = (
    "en-US",
    "es-ES",
    "ru-RU",
    "hi-IN",
    "fa-IR",
    "ar-SA",
    "zh-Hans-CN",
    "ja-JP",
    "ko-KR",
    "tr-TR",
    "id-ID",
    "sw-KE",
    "vi-VN",
    "th-TH",
    "ta-IN",
)
REQUIRED_BLOCK_IDS: tuple[str, ...] = (
    "country_intro",
    "country_risk_summary",
    "country_strength_summary",
)

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_URL_PATTERN = re.compile(r"\b\w+://")
_SECRET_KEYWORD_PATTERN = re.compile(
    r"(password|secret|api[_-]?key|private[_-]?key|access[_-]?token|"
    r"auth[_-]?token|bearer\s)",
    re.IGNORECASE,
)
_ALLOWED_URL_PREFIXES = (
    "synthetic://",
    "https://example.test",
    "http://example.test",
)


class LocaleCorpusError(RuntimeError):
    pass


def _ensure_safe(value: object, *, path: Path, context: str) -> None:
    """Reject real e-mails, non-reserved network addresses, and secret-like
    strings anywhere in the raw corpus payload, mirroring the world input
    safety gate (spec section 23, stage 1, item 6)."""
    if isinstance(value, str):
        if _EMAIL_PATTERN.search(value):
            raise LocaleCorpusError(
                f"{path}: {context} looks like a real e-mail address, "
                "which is not allowed in generator input"
            )
        for match in _URL_PATTERN.finditer(value):
            if not value[match.start() :].startswith(_ALLOWED_URL_PREFIXES):
                raise LocaleCorpusError(
                    f"{path}: {context} contains a network address, which "
                    "is not allowed in generator input"
                )
        if _SECRET_KEYWORD_PATTERN.search(value):
            raise LocaleCorpusError(
                f"{path}: {context} looks like a secret or credential, "
                "which is not allowed in generator input"
            )
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _ensure_safe(key, path=path, context=f"{context}.{key}")
            _ensure_safe(item, path=path, context=f"{context}.{key}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _ensure_safe(item, path=path, context=f"{context}[{index}]")


@dataclass(frozen=True)
class LocaleProfile:
    locale: str
    language_name: str
    script: str
    direction: str
    language_group: str

    @property
    def is_rtl(self) -> bool:
        return self.direction == "rtl"


@dataclass(frozen=True)
class LocaleTextPack:
    profile: LocaleProfile
    fictional_notice: str
    given_names: tuple[str, ...]
    family_names: tuple[str, ...]
    blocks: dict[str, tuple[str, ...]]
    comment_templates: tuple[str, ...]
    sample_short: str
    sample_long: str
    sample_diacritic: str
    sample_mixed: str
    sample_number: str
    sample_date: str

    @property
    def locale(self) -> str:
        return self.profile.locale

    @property
    def is_rtl(self) -> bool:
        return self.profile.is_rtl


@dataclass(frozen=True)
class LocaleCorpus:
    schema_version: str
    packs: tuple[LocaleTextPack, ...]
    source_checksum: str

    def by_locale(self, locale: str) -> LocaleTextPack:
        for pack in self.packs:
            if pack.locale == locale:
                return pack
        raise LocaleCorpusError(f"Unknown locale: {locale}")


def _mapping(value: object, *, field: str, path: Path) -> dict[str, object]:
    if not isinstance(value, dict):
        raise LocaleCorpusError(f"{path}: {field} must be an object")
    return value


def _string(value: object, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LocaleCorpusError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def _string_tuple(
    value: object, *, field: str, path: Path, minimum_length: int = 1
) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) < minimum_length:
        raise LocaleCorpusError(
            f"{path}: {field} must be a list with at least "
            f"{minimum_length} items"
        )
    return tuple(_string(item, field=field, path=path) for item in value)


def _load_blocks(
    value: object, *, field: str, path: Path
) -> dict[str, tuple[str, ...]]:
    payload = _mapping(value, field=field, path=path)
    missing = set(REQUIRED_BLOCK_IDS) - set(payload)
    if missing:
        raise LocaleCorpusError(
            f"{path}: {field} is missing blocks: {sorted(missing)}"
        )
    return {
        block_id: _string_tuple(
            payload.get(block_id),
            field=f"{field}.{block_id}",
            path=path,
            minimum_length=2,
        )
        for block_id in REQUIRED_BLOCK_IDS
    }


def _load_entry(payload: object, *, index: int, path: Path) -> LocaleTextPack:
    entry = _mapping(payload, field=f"locales[{index}]", path=path)
    locale = _string(entry.get("locale"), field="locale", path=path)
    direction = _string(entry.get("direction"), field="direction", path=path)
    if direction not in ("ltr", "rtl"):
        raise LocaleCorpusError(
            f"{path}: {locale}.direction must be 'ltr' or 'rtl'"
        )
    profile = LocaleProfile(
        locale=locale,
        language_name=_string(
            entry.get("language_name"), field="language_name", path=path
        ),
        script=_string(entry.get("script"), field="script", path=path),
        direction=direction,
        language_group=_string(
            entry.get("language_group"), field="language_group", path=path
        ),
    )
    return LocaleTextPack(
        profile=profile,
        fictional_notice=_string(
            entry.get("fictional_notice"),
            field="fictional_notice",
            path=path,
        ),
        given_names=_string_tuple(
            entry.get("given_names"),
            field="given_names",
            path=path,
            minimum_length=5,
        ),
        family_names=_string_tuple(
            entry.get("family_names"),
            field="family_names",
            path=path,
            minimum_length=5,
        ),
        blocks=_load_blocks(entry.get("blocks"), field="blocks", path=path),
        comment_templates=_string_tuple(
            entry.get("comment_templates"),
            field="comment_templates",
            path=path,
            minimum_length=2,
        ),
        sample_short=_string(
            entry.get("sample_short"), field="sample_short", path=path
        ),
        sample_long=_string(
            entry.get("sample_long"), field="sample_long", path=path
        ),
        sample_diacritic=_string(
            entry.get("sample_diacritic"),
            field="sample_diacritic",
            path=path,
        ),
        sample_mixed=_string(
            entry.get("sample_mixed"), field="sample_mixed", path=path
        ),
        sample_number=_string(
            entry.get("sample_number"), field="sample_number", path=path
        ),
        sample_date=_string(
            entry.get("sample_date"), field="sample_date", path=path
        ),
    )


def load_locale_corpus(
    path: Path = DEFAULT_LOCALE_CORPUS_FILE,
) -> LocaleCorpus:
    if not path.exists():
        raise LocaleCorpusError(f"Locale corpus file not found: {path}")

    raw_bytes = path.read_bytes()
    try:
        payload: object = json.loads(raw_bytes.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise LocaleCorpusError(f"{path}: input must be UTF-8") from error
    except json.JSONDecodeError as error:
        raise LocaleCorpusError(f"{path}: invalid JSON ({error})") from error

    _ensure_safe(payload, path=path, context="root")

    root = _mapping(payload, field="root", path=path)
    raw_locales = root.get("locales")
    if not isinstance(raw_locales, list) or not raw_locales:
        raise LocaleCorpusError(f"{path}: locales must be a non-empty list")

    packs = tuple(
        _load_entry(entry, index=index, path=path)
        for index, entry in enumerate(raw_locales)
    )
    locale_codes = [pack.locale for pack in packs]
    if len(set(locale_codes)) != len(locale_codes):
        raise LocaleCorpusError(f"{path}: locale codes must be unique")
    missing = set(REQUIRED_LOCALES) - set(locale_codes)
    unexpected = set(locale_codes) - set(REQUIRED_LOCALES)
    if missing or unexpected:
        raise LocaleCorpusError(
            f"{path}: locales must exactly match the required 15-locale "
            f"matrix; missing={sorted(missing)}, unexpected={sorted(unexpected)}"
        )

    return LocaleCorpus(
        schema_version=_string(
            root.get("schema_version"), field="schema_version", path=path
        ),
        packs=packs,
        source_checksum=hashlib.sha256(raw_bytes).hexdigest(),
    )
