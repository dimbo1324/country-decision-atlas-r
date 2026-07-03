"""Unit tests for the full-check quality-gate script: log sanitization, safe env defaults, and profile phase selection."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


def load_full_check_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "scripts" / "dev_tools" / "full_check.py"
    spec = importlib.util.spec_from_file_location("full_check_script", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_args(**overrides: Any) -> argparse.Namespace:
    defaults = {
        "profile": "full",
        "doctor": False,
        "fix": False,
        "skip_docker": False,
        "skip_e2e": False,
        "skip_precommit": False,
        "quiet": True,
        "docker_max_attempts": 1,
        "docker_retry_initial_delay": 0,
        "docker_retry_delay_step": 0,
        "admin_token": "",
        "config": "",
        "regen_proto": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_sanitize_log_line_masks_known_secrets() -> None:
    module = load_full_check_module()

    line = (
        "ADMIN_TOKEN=abc DATABASE_URL=postgresql://user:pass@host/db "
        "TELEGRAM_BOT_TOKEN: 123 JWT_SECRET=secret"
    )

    sanitized = module.sanitize_log_line(line)

    assert "abc" not in sanitized
    assert "pass@host" not in sanitized
    assert "123" not in sanitized
    assert "secret" not in sanitized
    assert "ADMIN_TOKEN=<redacted>" in sanitized


def test_pnpm_safe_env_sets_non_interactive_defaults() -> None:
    module = load_full_check_module()

    env = module.pnpm_safe_env()

    assert env["CI"] == "true"
    assert env["pnpm_config_confirmModulesPurge"] == "false"
    assert env["pnpm_config_verify_deps_before_run"] == "false"


def test_doctor_only_runs_read_only_phases() -> None:
    module = load_full_check_module()

    checker = module.FullCheck(make_args(doctor=True, profile="full"))

    assert checker.should_run_phase("diagnostics")
    assert checker.should_run_phase("toolchain")
    assert checker.should_run_phase("git_status")
    assert not checker.should_run_phase("dependencies")
    assert not checker.should_run_phase("docker")
    checker.out.close()


def test_quick_profile_keeps_docker_out_of_daily_loop() -> None:
    module = load_full_check_module()

    checker = module.FullCheck(make_args(profile="quick"))

    assert checker.should_run_phase("static_quality")
    assert not checker.should_run_phase("dependencies")
    assert not checker.should_run_phase("docker")
    assert not checker.should_run_phase("precommit")
    checker.out.close()
