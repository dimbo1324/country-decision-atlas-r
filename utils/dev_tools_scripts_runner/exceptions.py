"""Exception types for the dev-tools script orchestrator."""

from __future__ import annotations


class RunnerError(Exception):
    """Base class for every error this package raises on purpose."""


class ConfigValidationError(RunnerError):
    """Raised when a config JSON file is missing, malformed, or internally
    inconsistent (unknown category reference, duplicate script identifier,
    a cadence/cadence_ref conflict, a script path that would escape the
    project root). Config is hand-edited, so failures here must say
    exactly what is wrong and where -- never surface as a generic
    KeyError/TypeError deep inside menu rendering."""


class ScriptNotFoundError(RunnerError):
    """Raised when a script registered in scripts.json has no file on
    disk at its resolved path."""
