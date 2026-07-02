from __future__ import annotations

import argparse
from collections.abc import Callable
import contextlib
import ctypes
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import re
import secrets
import shutil
import socket
import subprocess
import sys
import time
from typing import Any
import urllib.error
import urllib.request


REPO_ROOT = Path(__file__).resolve().parent

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

DEFAULT_TOOL_BASELINES: list[dict[str, Any]] = [
    {
        "name": "Git",
        "command": "git",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "2.40.0",
        "severity": "required",
        "install_hint": "Install or upgrade Git: https://git-scm.com/downloads (winget install --id Git.Git -e)",
    },
    {
        "name": "Docker Engine",
        "command": "docker",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "24.0.0",
        "severity": "required",
        "install_hint": "Install Docker Desktop: https://www.docker.com/products/docker-desktop/",
    },
    {
        "name": "Docker Compose",
        "command": "docker",
        "version_args": ["compose", "version"],
        "version_pattern": r"v?(\d+\.\d+\.\d+)",
        "recommended_min_version": "2.20.0",
        "severity": "required",
        "install_hint": "Docker Compose ships with Docker Desktop. Standalone install: https://docs.docker.com/compose/install/",
    },
    {
        "name": "Node.js",
        "command": "node",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "20.0.0",
        "severity": "required",
        "install_hint": "Install Node.js LTS: https://nodejs.org/en/download (winget install --id OpenJS.NodeJS.LTS -e)",
    },
    {
        "name": "Corepack",
        "command": "corepack",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "0.20.0",
        "severity": "optional",
        "install_hint": "Corepack ships with Node.js 16.9+. If missing: npm install -g corepack && corepack enable",
    },
    {
        "name": "protoc",
        "command": "protoc",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+)",
        "recommended_min_version": "25.0",
        "severity": "required",
        "install_hint": "Install protoc: https://github.com/protocolbuffers/protobuf/releases (winget install --id Google.Protobuf -e, or choco install protoc)",
    },
    {
        "name": "protoc-gen-go",
        "command": "protoc-gen-go",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "1.31.0",
        "severity": "required",
        "install_hint": "Install: go install google.golang.org/protobuf/cmd/protoc-gen-go@latest (then ensure %GOPATH%\\bin is on PATH)",
    },
    {
        "name": "protoc-gen-go-grpc",
        "command": "protoc-gen-go-grpc",
        "version_args": ["--version"],
        "version_pattern": r"(\d+\.\d+\.\d+)",
        "recommended_min_version": "1.3.0",
        "severity": "required",
        "install_hint": "Install: go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest (then ensure %GOPATH%\\bin is on PATH)",
    },
]

DEFAULT_NETWORK_CHECKS: list[dict[str, Any]] = [
    {"name": "npm registry", "host": "registry.npmjs.org", "port": 443},
    {"name": "PyPI", "host": "pypi.org", "port": 443},
    {"name": "Docker Hub", "host": "registry-1.docker.io", "port": 443},
    {"name": "GitHub", "host": "github.com", "port": 443},
]

DEFAULT_MIN_FREE_DISK_GB = 5

SMOKE_URLS = [
    "http://localhost:8000/health",
    "http://localhost:8000/ready",
    "http://localhost:8000/api/v1/countries?locale=ru",
    "http://localhost:8000/api/v1/countries/russia/trust?locale=ru",
    "http://localhost:8000/api/v1/countries/uruguay/trust?locale=ru",
    "http://localhost:8000/api/v1/countries/argentina/trust?locale=ru",
    "http://localhost:8000/api/v1/search?q=residence&locale=ru",
]

STALE_CACHE_DIRS = [".pytest_cache", ".mypy_cache", ".ruff_cache"]


@dataclass
class StageResult:
    stage: str
    status: str
    detail: str = ""
    duration_seconds: float = 0.0


@dataclass
class Recommendation:
    tool: str
    issue: str
    hint: str = ""


@dataclass
class NetworkResult:
    name: str
    host: str
    port: int
    reachable: bool


class DualWriter:
    def __init__(self, transcript_path: Path) -> None:
        self.console = sys.stdout
        self.file = transcript_path.open("a", encoding="utf-8")

    def write_line(self, plain_text: str, console_text: str | None = None) -> None:
        self.console.write(
            (console_text if console_text is not None else plain_text) + "\n"
        )
        self.console.flush()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.file.write(f"[{timestamp}] {plain_text}\n")
        self.file.flush()

    def close(self) -> None:
        self.file.close()


def enable_windows_ansi() -> bool:
    if platform.system() != "Windows":
        return True
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        enable_virtual_terminal_processing = 0x0004
        return bool(
            kernel32.SetConsoleMode(
                handle, mode.value | enable_virtual_terminal_processing
            )
        )
    except Exception:
        return False


def compare_semver(actual: str, required: str) -> int:
    def parse(value: str) -> tuple[int, ...] | None:
        parts = re.findall(r"\d+", value)
        return tuple(int(p) for p in parts) if parts else None

    a, r = parse(actual), parse(required)
    if a is None or r is None:
        return (actual > required) - (actual < required)
    length = max(len(a), len(r))
    a = a + (0,) * (length - len(a))
    r = r + (0,) * (length - len(r))
    return (a > r) - (a < r)


class WindowsMemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def windows_memory_gb() -> tuple[float | None, float | None]:
    try:
        stat = WindowsMemoryStatusEx()
        stat.dwLength = ctypes.sizeof(WindowsMemoryStatusEx)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        if not ok:
            return None, None
        total_gb = round(stat.ullTotalPhys / 1_073_741_824, 1)
        free_gb = round(stat.ullAvailPhys / 1_073_741_824, 1)
        return total_gb, free_gb
    except Exception:
        return None, None


def get_system_diagnostics() -> dict[str, Any]:
    diag: dict[str, Any] = {
        "hostname": "unknown",
        "os_caption": "unknown",
        "os_architecture": "unknown",
        "processor_count": os.cpu_count() or 0,
        "total_memory_gb": None,
        "free_memory_gb": None,
        "repo_drive_free_gb": None,
        "python_version": platform.python_version(),
    }
    with contextlib.suppress(OSError):
        diag["hostname"] = socket.gethostname()
    try:
        diag["os_caption"] = platform.platform()
        diag["os_architecture"] = platform.machine()
    except Exception:
        pass
    if platform.system() == "Windows":
        total_gb, free_gb = windows_memory_gb()
        diag["total_memory_gb"] = total_gb
        diag["free_memory_gb"] = free_gb
    try:
        usage = shutil.disk_usage(REPO_ROOT)
        diag["repo_drive_free_gb"] = round(usage.free / 1_000_000_000, 1)
    except OSError:
        pass
    return diag


def get_git_context() -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "branch": "unknown",
        "commit": "unknown",
        "dirty_file_count": None,
        "ahead_behind": "unknown",
    }
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            ctx["branch"] = r.stdout.strip()
    except OSError:
        pass
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            ctx["commit"] = r.stdout.strip()
    except OSError:
        pass
    try:
        r = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        ctx["dirty_file_count"] = len(
            [line for line in r.stdout.splitlines() if line.strip()]
        )
    except OSError:
        pass
    try:
        r = subprocess.run(
            [
                "git",
                "rev-list",
                "--left-right",
                "--count",
                f"origin/{ctx['branch']}...{ctx['branch']}",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = r.stdout.strip().split()
            if len(parts) == 2:
                ctx["ahead_behind"] = f"behind={parts[0]} ahead={parts[1]}"
    except OSError:
        pass
    return ctx


def get_pyproject_exact_pin(package_name: str) -> str | None:
    try:
        content = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(rf'"{re.escape(package_name)}==([0-9.]+)"', content)
        return match.group(1) if match else None
    except OSError:
        return None


def get_requires_python_min_version() -> str:
    try:
        content = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'requires-python\s*=\s*"[>=]+([0-9.]+)"', content)
        if match:
            v = match.group(1)
            if v.count(".") == 1:
                v += ".0"
            return v
    except OSError:
        pass
    return "3.12.0"


def get_package_json() -> dict[str, Any] | None:
    try:
        data = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def get_go_mod_min_version() -> str:
    try:
        content = (REPO_ROOT / "apps" / "notifier" / "go.mod").read_text(
            encoding="utf-8"
        )
        match = re.search(r"(?m)^go (\d+\.\d+(?:\.\d+)?)", content)
        if match:
            v = match.group(1)
            if v.count(".") == 1:
                v += ".0"
            return v
    except OSError:
        pass
    return "1.25.0"


def wait_for_http_health(url: str, timeout_seconds: int = 90) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        time.sleep(2)
    return False


def test_port_reachable(host: str, port: int, timeout: float = 3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


class FullCheck:
    def __init__(self, args: argparse.Namespace) -> None:
        self.skip_docker = args.skip_docker
        self.skip_e2e = args.skip_e2e
        self.skip_precommit = args.skip_precommit
        self.quiet = args.quiet
        self.docker_max_attempts = args.docker_max_attempts
        self.docker_retry_initial_delay = args.docker_retry_initial_delay
        self.docker_retry_delay_step = args.docker_retry_delay_step
        self.admin_token = args.admin_token
        self.config_path = args.config
        self.regen_proto = args.regen_proto

        self.run_timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.report_dir = REPO_ROOT / "full-check-reports" / self.run_timestamp
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_path = self.report_dir / "transcript.log"
        self.summary_path = self.report_dir / "summary.txt"
        self.report_json_path = self.report_dir / "report.json"
        self.recommendations_path = self.report_dir / "recommendations.txt"

        self.out = DualWriter(self.transcript_path)
        self.color_enabled = sys.stdout.isatty() and enable_windows_ansi()

        self.stage_results: list[StageResult] = []
        self.recommendations: list[Recommendation] = []
        self.network_results: list[NetworkResult] = []
        self.started_at = datetime.now()
        self.system_info: dict[str, Any] = {}
        self.git_context: dict[str, Any] = {}
        self.go_tooling_present = False
        self.python312: list[str] | None = None

    def colorize(self, text: str, color: str | None) -> str:
        if not color or not self.color_enabled:
            return text
        return f"{color}{text}{RESET}"

    def log(self, message: str, level: str = "info") -> None:
        color = {
            "info": None,
            "warn": YELLOW,
            "error": RED,
            "ok": GREEN,
            "section": CYAN,
        }.get(level)
        self.out.write_line(message, self.colorize(message, color))

    def raw(self, line: str) -> None:
        self.out.write_line(line)

    def section(self, title: str) -> None:
        if self.quiet:
            self.log(f">> {title}", "section")
            return
        bar = "=" * 78
        self.log("")
        self.log(bar, "section")
        self.log(title, "section")
        self.log(bar, "section")

    def add_stage_result(
        self, stage: str, status: str, detail: str = "", duration_seconds: float = 0.0
    ) -> None:
        self.stage_results.append(
            StageResult(stage, status, detail, round(duration_seconds, 1))
        )
        if self.quiet and status == "OK":
            return
        level = {"OK": "ok", "FAIL": "error", "SKIP": "warn", "WARN": "warn"}.get(
            status, "info"
        )
        duration_text = (
            f" ({round(duration_seconds, 1)}s)" if duration_seconds >= 1 else ""
        )
        self.log(f"  [{status}] {stage} {detail}{duration_text}", level)

    def add_recommendation(self, tool: str, issue: str, hint: str = "") -> None:
        self.recommendations.append(Recommendation(tool, issue, hint))

    def run_streaming(
        self,
        exe_args: list[str],
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> int:
        try:
            process = subprocess.Popen(
                exe_args,
                cwd=str(cwd or REPO_ROOT),
                env=env or os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as exc:
            self.log(f"  ERROR invoking '{exe_args[0]}': {exc}", "error")
            return -1
        assert process.stdout is not None
        for line in process.stdout:
            self.raw(line.rstrip("\n"))
        process.wait()
        return process.returncode

    def run_gate_step(
        self, name: str, exe_args: list[str] | None, cwd: Path | None = None
    ) -> int:
        if exe_args is None:
            self.add_stage_result(name, "SKIP", "required executable not found")
            return -1
        start = time.monotonic()
        exit_code = self.run_streaming(exe_args, cwd=cwd)
        duration = time.monotonic() - start
        self.add_stage_result(
            name, "OK" if exit_code == 0 else "FAIL", duration_seconds=duration
        )
        return exit_code

    def run_with_retry(
        self,
        description: str,
        func: Callable[[], int],
        max_attempts: int,
        initial_delay: int,
        delay_step: int,
    ) -> int:
        attempt = 1
        delay = initial_delay
        while True:
            self.log(f"  attempt {attempt}/{max_attempts}: {description}")
            try:
                exit_code = func()
            except Exception as exc:
                self.log(f"  attempt {attempt} threw an exception: {exc}", "warn")
                exit_code = -1
            if exit_code == 0:
                return 0
            if attempt >= max_attempts:
                self.log(
                    f"  giving up after {attempt} attempts: {description}", "error"
                )
                return exit_code
            self.log(
                f"  attempt {attempt} failed (exit {exit_code}), waiting {delay}s before retry...",
                "warn",
            )
            time.sleep(delay)
            delay += delay_step
            attempt += 1

    def get_tool_version_string(self, exe_args: list[str], pattern: str) -> str | None:
        try:
            result = subprocess.run(
                exe_args,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
        except Exception:
            return None
        combined = (result.stdout or "") + (result.stderr or "")
        match = re.search(pattern, combined)
        return match.group(1) if match else None

    def check_tool_version(
        self,
        name: str,
        command: str,
        version_args: list[str],
        pattern: str,
        recommended: str = "",
        mode: str = "min",
        severity: str = "required",
        install_hint: str = "",
    ) -> bool:
        exe = shutil.which(command)
        if not exe:
            status = "FAIL" if severity == "required" else "WARN"
            self.add_stage_result(name, status, f"command not found: {command}")
            if install_hint:
                self.add_recommendation(name, "not installed", install_hint)
            return False

        version = self.get_tool_version_string([exe, *version_args], pattern)

        if mode == "presence":
            self.add_stage_result(name, "OK", f"found ({command}), version={version}")
            return True
        if not version:
            self.add_stage_result(
                name,
                "WARN",
                f"found ({command}) but could not parse a version string; assuming compatible",
            )
            return True
        if mode == "exact":
            if not recommended or version == recommended:
                self.add_stage_result(name, "OK", f"version={version}")
                return True
            self.add_stage_result(
                name,
                "WARN",
                f"version={version}, project manifest pins {recommended} "
                "(informational; pip/pnpm normally enforces this automatically)",
            )
            self.add_recommendation(
                name,
                f"installed version ({version}) differs from the manifest pin ({recommended})",
                "Re-run dependency install for this project; if it persists, check for a conflicting "
                "global/site-packages install.",
            )
            return True

        cmp_result = compare_semver(version, recommended)
        if not recommended or cmp_result >= 0:
            self.add_stage_result(name, "OK", f"version={version}")
            return True
        self.add_stage_result(
            name,
            "WARN",
            f"version={version} is older than the verified baseline ({recommended}); likely still compatible",
        )
        if install_hint:
            self.add_recommendation(
                name,
                f"version {version} is older than the recommended baseline {recommended}",
                install_hint,
            )
        return True

    def load_config(self) -> dict[str, Any]:
        defaults = {
            "tools": DEFAULT_TOOL_BASELINES,
            "network_checks": DEFAULT_NETWORK_CHECKS,
            "min_free_disk_space_gb": DEFAULT_MIN_FREE_DISK_GB,
        }
        if not self.config_path:
            return defaults
        path = Path(self.config_path)
        if not path.exists():
            self.log(
                f"WARNING: config file not found at {path}; using built-in defaults.",
                "warn",
            )
            return defaults
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            tools = [
                {
                    "name": t.get("name"),
                    "command": t.get("command"),
                    "version_args": t.get("versionArgs", []),
                    "version_pattern": t.get("versionPattern", r"(\d+\.\d+\.\d+)"),
                    "recommended_min_version": t.get("recommendedMinVersion", ""),
                    "severity": t.get("severity", "required"),
                    "install_hint": t.get("installHint", ""),
                }
                for t in data.get("tools", [])
            ]
            return {
                "tools": tools or DEFAULT_TOOL_BASELINES,
                "network_checks": data.get("networkChecks", DEFAULT_NETWORK_CHECKS),
                "min_free_disk_space_gb": data.get(
                    "minFreeDiskSpaceGb", DEFAULT_MIN_FREE_DISK_GB
                ),
            }
        except Exception as exc:
            self.log(
                f"WARNING: failed to parse {path}: {exc}. Using built-in defaults.",
                "warn",
            )
            return defaults

    def resolve_python312(self) -> list[str] | None:
        py_launcher = shutil.which("py")
        if py_launcher:
            probe = subprocess.run(
                [py_launcher, "-3.12", "--version"], capture_output=True, text=True
            )
            if probe.returncode == 0:
                return [py_launcher, "-3.12"]
        for candidate in ("python3.12", "python3", "python"):
            exe = shutil.which(candidate)
            if exe:
                return [exe]
        return None

    def phase_diagnostics(self, config: dict[str, Any]) -> None:
        self.section("Phase -1 — Diagnostics (system, git, network)")

        self.system_info = get_system_diagnostics()
        self.log(
            "  host={} os={} ({}) cpu={} ram={}GB free-ram={}GB free-disk={}GB python={}".format(
                self.system_info["hostname"],
                self.system_info["os_caption"],
                self.system_info["os_architecture"],
                self.system_info["processor_count"],
                self.system_info["total_memory_gb"],
                self.system_info["free_memory_gb"],
                self.system_info["repo_drive_free_gb"],
                self.system_info["python_version"],
            )
        )

        self.git_context = get_git_context()
        self.log(
            "  git branch={} commit={} dirty-files={} {}".format(
                self.git_context["branch"],
                self.git_context["commit"],
                self.git_context["dirty_file_count"],
                self.git_context["ahead_behind"],
            )
        )

        min_free_gb = config["min_free_disk_space_gb"]
        free_gb = self.system_info["repo_drive_free_gb"]
        if free_gb is not None and free_gb < min_free_gb:
            self.add_stage_result(
                "Disk space",
                "WARN",
                f"only {free_gb} GB free on the repo drive (recommended >= {min_free_gb} GB); "
                "Docker builds and node_modules installs may fail or behave unpredictably",
            )
            self.add_recommendation(
                "Disk space",
                f"low free disk space ({free_gb} GB)",
                "Free up disk space (Docker images/containers: 'docker system prune'; old node_modules; "
                "Windows Disk Cleanup) before running Docker-heavy phases.",
            )
        else:
            self.add_stage_result("Disk space", "OK", f"{free_gb} GB free")

        for net in config["network_checks"]:
            reachable = test_port_reachable(net["host"], net["port"], timeout=3.0)
            self.network_results.append(
                NetworkResult(net["name"], net["host"], net["port"], reachable)
            )
            if reachable:
                self.add_stage_result(
                    f"Network: {net['name']}",
                    "OK",
                    f"{net['host']}:{net['port']} reachable",
                )
            else:
                self.add_stage_result(
                    f"Network: {net['name']}",
                    "WARN",
                    f"{net['host']}:{net['port']} not reachable (timeout or blocked)",
                )
                self.add_recommendation(
                    f"Network: {net['name']}",
                    f"could not reach {net['host']}:{net['port']}",
                    "Check internet connection, VPN, proxy, or corporate firewall settings. Installs that "
                    "need this host may fail or need more retries.",
                )

        for stale_dir in STALE_CACHE_DIRS:
            stale_path = REPO_ROOT / stale_dir
            if stale_path.exists():
                shutil.rmtree(stale_path, ignore_errors=True)
                if stale_path.exists():
                    self.add_stage_result(
                        f"Stale cache: {stale_dir}",
                        "WARN",
                        "exists and could not be removed (likely locked by another process); may cause "
                        "unrelated-looking prettier/pytest failures later",
                    )
                    self.add_recommendation(
                        stale_dir,
                        "directory is locked and could not be cleaned",
                        f"Close any IDE, antivirus scan, or leftover process that may be holding '{stale_dir}' "
                        "open, then re-run this script.",
                    )

    def phase_toolchain(self, config: dict[str, Any]) -> None:
        self.section("Phase 0 — System toolchain verification")

        package_json = get_package_json()
        pnpm_required = playwright_required = prettier_required = (
            openapi_ts_required
        ) = None
        if package_json:
            if package_json.get("packageManager"):
                pnpm_required = package_json["packageManager"].split("@")[-1]
            dev_deps = package_json.get("devDependencies", {})
            if dev_deps.get("@playwright/test"):
                playwright_required = re.sub(r"[\^~]", "", dev_deps["@playwright/test"])
            if dev_deps.get("prettier"):
                prettier_required = re.sub(r"[\^~]", "", dev_deps["prettier"])
            if dev_deps.get("openapi-typescript"):
                openapi_ts_required = re.sub(
                    r"[\^~]", "", dev_deps["openapi-typescript"]
                )
        else:
            self.add_stage_result(
                "package.json",
                "WARN",
                "could not be read/parsed; pnpm/Next/Playwright/Prettier/openapi-typescript baselines unavailable this run",
            )

        self.fastapi_required = get_pyproject_exact_pin("fastapi")
        self.pydantic_required = get_pyproject_exact_pin("pydantic")
        python_required = get_requires_python_min_version()
        go_required = get_go_mod_min_version()
        self.pnpm_required = pnpm_required
        self.playwright_required = playwright_required
        self.prettier_required = prettier_required
        self.openapi_ts_required = openapi_ts_required

        self.check_tool_version(
            "Python 3.12",
            "py",
            ["-3.12", "--version"],
            r"(\d+\.\d+\.\d+)",
            recommended=python_required,
            mode="min",
            severity="required",
            install_hint="https://www.python.org/downloads/ (winget install --id Python.Python.3.12 -e)",
        )
        self.check_tool_version(
            "pnpm",
            "pnpm",
            ["--version"],
            r"(\d+\.\d+\.\d+)",
            recommended=pnpm_required or "",
            mode="min",
            severity="required",
            install_hint="corepack enable && corepack prepare pnpm@latest --activate (https://pnpm.io/installation)",
        )
        self.check_tool_version(
            "Go",
            "go",
            ["version"],
            r"go(\d+\.\d+\.\d+)",
            recommended=go_required,
            mode="min",
            severity="required",
            install_hint="https://go.dev/dl/",
        )

        for tool in config["tools"]:
            self.check_tool_version(
                tool["name"],
                tool["command"],
                tool["version_args"],
                tool["version_pattern"],
                recommended=tool.get("recommended_min_version", ""),
                mode="min",
                severity=tool.get("severity", "required"),
                install_hint=tool.get("install_hint", ""),
            )

        self.go_tooling_present = all(
            shutil.which(cmd)
            for cmd in ("go", "protoc", "protoc-gen-go", "protoc-gen-go-grpc")
        )

    def phase_dependencies(self) -> None:
        self.section("Phase 1 — Dependency installation")

        if not self.admin_token:
            self.admin_token = "local-gate-" + secrets.token_hex(8)
        os.environ["ADMIN_TOKEN"] = self.admin_token
        self.log(
            f"Using ADMIN_TOKEN={self.admin_token[:16]}... for this run (API container and test runner share it)."
        )

        self.python312 = self.resolve_python312()
        python312 = self.python312
        if not python312:
            self.add_stage_result(
                "pip install -e .[dev]",
                "FAIL",
                "no usable Python 3.12 interpreter found",
            )
            self.add_recommendation(
                "Python 3.12",
                "no usable interpreter found",
                "Install Python 3.12 and ensure 'py' or 'python3.12' is on PATH.",
            )
        else:
            pip_result = self.run_with_retry(
                "pip install -e .[dev]",
                lambda: self.run_streaming(
                    [*python312, "-m", "pip", "install", "-e", ".[dev]"]
                ),
                max_attempts=3,
                initial_delay=5,
                delay_step=5,
            )
            self.add_stage_result(
                "pip install -e .[dev]", "OK" if pip_result == 0 else "FAIL"
            )
            if pip_result != 0:
                self.add_recommendation(
                    "pip install -e .[dev]",
                    "install failed",
                    "Check the transcript above for the pip error. Common causes: no internet, a locked "
                    "virtualenv, or a Python version mismatch (project requires >= 3.12).",
                )

        pnpm_exe = shutil.which("pnpm")
        pnpm_result = self.run_with_retry(
            "pnpm install",
            lambda: self.run_streaming([pnpm_exe, "install"]) if pnpm_exe else -1,
            max_attempts=3,
            initial_delay=5,
            delay_step=5,
        )
        self.add_stage_result("pnpm install", "OK" if pnpm_result == 0 else "FAIL")
        if pnpm_result != 0:
            self.add_recommendation(
                "pnpm install",
                "install failed",
                "Check the transcript above. Common causes: no internet/registry access, or a stale "
                "pnpm-lock.yaml conflict (try 'pnpm install --no-frozen-lockfile').",
            )

        playwright_result = self.run_with_retry(
            "pnpm exec playwright install chromium",
            lambda: (
                self.run_streaming(
                    [pnpm_exe, "exec", "playwright", "install", "chromium"]
                )
                if pnpm_exe
                else -1
            ),
            max_attempts=3,
            initial_delay=5,
            delay_step=5,
        )
        self.add_stage_result(
            "playwright install chromium", "OK" if playwright_result == 0 else "FAIL"
        )

    def phase_pinned_versions(self) -> None:
        self.section("Phase 2 — Project-pinned version verification")

        if self.python312:
            self.check_tool_version(
                "FastAPI (pip)",
                self.python312[0],
                [
                    *self.python312[1:],
                    "-c",
                    "import fastapi; print(fastapi.__version__)",
                ],
                r"(\d+\.\d+\.\d+)",
                recommended=self.fastapi_required or "",
                mode="exact",
                severity="optional",
            )
            self.check_tool_version(
                "Pydantic (pip)",
                self.python312[0],
                [
                    *self.python312[1:],
                    "-c",
                    "import pydantic; print(pydantic.__version__)",
                ],
                r"(\d+\.\d+\.\d+)",
                recommended=self.pydantic_required or "",
                mode="exact",
                severity="optional",
            )

        pnpm_exe = shutil.which("pnpm")
        if pnpm_exe:
            self.check_tool_version(
                "Next.js",
                pnpm_exe,
                [
                    "--filter",
                    "@country-decision-atlas/web",
                    "exec",
                    "next",
                    "--version",
                ],
                r"(\d+\.\d+\.\d+)",
                recommended="15.0.0",
                mode="min",
                severity="optional",
            )
            self.check_tool_version(
                "Playwright",
                pnpm_exe,
                ["exec", "playwright", "--version"],
                r"(\d+\.\d+\.\d+)",
                recommended=self.playwright_required or "",
                mode="min",
                severity="optional",
            )
            self.check_tool_version(
                "Prettier",
                pnpm_exe,
                ["exec", "prettier", "--version"],
                r"(\d+\.\d+\.\d+)",
                recommended=self.prettier_required or "",
                mode="min",
                severity="optional",
            )
            self.check_tool_version(
                "openapi-typescript",
                pnpm_exe,
                ["exec", "openapi-typescript", "--version"],
                r"(\d+\.\d+\.\d+)",
                recommended=self.openapi_ts_required or "",
                mode="min",
                severity="optional",
            )

    def phase_static_quality(self) -> None:
        self.section("Phase 3 — Static quality gate")
        py312 = self.python312

        def py_args(*parts: str) -> list[str] | None:
            return [*py312, *parts] if py312 else None

        self.run_gate_step(
            "ruff check",
            py_args("-m", "ruff", "check", "apps", "packages", "scripts", "tests"),
        )
        self.run_gate_step(
            "ruff format --check",
            py_args(
                "-m",
                "ruff",
                "format",
                "--check",
                "apps",
                "packages",
                "scripts",
                "tests",
            ),
        )
        self.run_gate_step(
            "mypy", py_args("-m", "mypy", "apps", "packages", "scripts", "tests")
        )
        self.run_gate_step(
            "sqlfluff lint",
            py_args("-m", "sqlfluff", "lint", "database", "--dialect", "postgres"),
        )

        (REPO_ROOT / ".tmp" / "pytest").mkdir(parents=True, exist_ok=True)
        self.run_gate_step(
            "pytest",
            py_args("-m", "pytest", "-p", "no:cacheprovider", "--basetemp=.tmp/pytest"),
        )

        pnpm_exe = shutil.which("pnpm")

        def pnpm_args(*parts: str) -> list[str] | None:
            return [pnpm_exe, *parts] if pnpm_exe else None

        self.run_gate_step("pnpm contracts:generate", pnpm_args("contracts:generate"))
        self.run_gate_step("pnpm quality", pnpm_args("quality"))

    def phase_go_notifier(self) -> None:
        self.section("Phase 4 — Go notifier gate")
        if not self.go_tooling_present:
            self.add_stage_result(
                "Go notifier gate",
                "SKIP",
                "go/protoc/protoc-gen-go/protoc-gen-go-grpc not all present; see Phase 0 recommendations above",
            )
            return

        notifier_dir = REPO_ROOT / "apps" / "notifier"
        protoc_exe = shutil.which("protoc")
        go_exe = shutil.which("go")

        if self.regen_proto:
            self.run_gate_step(
                "protoc generate",
                [
                    protoc_exe,
                    "-I",
                    ".",
                    "--go_out=.",
                    "--go_opt=module=github.com/country-decision-atlas/notifier",
                    "--go-grpc_out=.",
                    "--go-grpc_opt=module=github.com/country-decision-atlas/notifier",
                    "proto/subscriptions.proto",
                ]
                if protoc_exe
                else None,
                cwd=notifier_dir,
            )
            git_exe = shutil.which("git")
            if git_exe:
                pb_dir = notifier_dir / "internal" / "grpc" / "pb"
                diff_exit = self.run_streaming(
                    [git_exe, "diff", "--quiet", "--", str(pb_dir)]
                )
                if diff_exit != 0:
                    self.add_stage_result(
                        "protoc generate produced a diff",
                        "WARN",
                        "regenerated .pb.go differs from the committed version (often just a "
                        "protoc/protoc-gen-go version header); revert with 'git checkout -- "
                        f"{pb_dir}' unless proto/subscriptions.proto actually changed",
                    )
                    self.add_recommendation(
                        "protoc generate",
                        "regenerated .pb.go differs from committed version",
                        f"If proto/subscriptions.proto did not change, run: git checkout -- {pb_dir}",
                    )
        else:
            self.add_stage_result(
                "protoc generate",
                "SKIP",
                "pass --regen-proto to regenerate; committed .pb.go files are used as-is "
                "(Docker build has no codegen step and requires them to be tracked)",
            )

        self.run_gate_step(
            "go vet", [go_exe, "vet", "./..."] if go_exe else None, cwd=notifier_dir
        )
        self.run_gate_step(
            "go test", [go_exe, "test", "./..."] if go_exe else None, cwd=notifier_dir
        )

    def phase_docker(self) -> None:
        if self.skip_docker:
            self.add_stage_result(
                "Docker stack / migrations / runtime smoke / E2E",
                "SKIP",
                "--skip-docker was set",
            )
            return

        self.section("Phase 5 — Docker stack, migrations, runtime smoke")
        docker_exe = shutil.which("docker")
        if not docker_exe:
            self.add_stage_result(
                "Docker stack / migrations / runtime smoke / E2E",
                "SKIP",
                "docker command not found; see Phase 0 recommendations",
            )
            return

        docker_info_exit = self.run_streaming([docker_exe, "info"])
        if docker_info_exit != 0:
            self.add_stage_result(
                "docker daemon reachable",
                "SKIP",
                "Docker Desktop is not running; skipping all Docker-dependent steps",
            )
            return
        self.add_stage_result("docker daemon reachable", "OK")

        docker_up_exit = self.run_with_retry(
            "docker compose up --build -d api",
            lambda: self.run_streaming(
                [docker_exe, "compose", "up", "--build", "-d", "api"]
            ),
            max_attempts=self.docker_max_attempts,
            initial_delay=self.docker_retry_initial_delay,
            delay_step=self.docker_retry_delay_step,
        )
        self.add_stage_result(
            "docker compose up --build -d api", "OK" if docker_up_exit == 0 else "FAIL"
        )
        if docker_up_exit != 0:
            self.add_recommendation(
                "Docker build",
                f"docker compose up --build failed after {self.docker_max_attempts} attempts",
                "Check Docker Desktop is running with enough resources (Settings > Resources), check disk "
                "space, and inspect the transcript for the underlying build error.",
            )
            self.add_stage_result(
                "migrations / bootstrap / smoke / E2E",
                "SKIP",
                f"docker compose up failed after {self.docker_max_attempts} attempts",
            )
            return

        api_healthy = wait_for_http_health(
            "http://localhost:8000/health", timeout_seconds=90
        )
        self.add_stage_result(
            "API health endpoint reachable", "OK" if api_healthy else "FAIL"
        )
        if not api_healthy:
            self.add_stage_result(
                "migrations / bootstrap / smoke / E2E",
                "SKIP",
                "API never became healthy",
            )
            return

        mig1 = self.run_streaming(
            [
                docker_exe,
                "compose",
                "exec",
                "-T",
                "api",
                "python",
                "scripts/apply_migrations.py",
            ]
        )
        self.add_stage_result(
            "apply_migrations.py (first run)", "OK" if mig1 == 0 else "FAIL"
        )

        mig2 = self.run_streaming(
            [
                docker_exe,
                "compose",
                "exec",
                "-T",
                "api",
                "python",
                "scripts/apply_migrations.py",
            ]
        )
        self.add_stage_result(
            "apply_migrations.py (idempotency rerun)", "OK" if mig2 == 0 else "FAIL"
        )

        bootstrap_exit = self.run_streaming(
            [
                docker_exe,
                "compose",
                "exec",
                "-T",
                "api",
                "python",
                "scripts/bootstrap_runtime_read_models.py",
            ]
        )
        self.add_stage_result(
            "bootstrap_runtime_read_models.py", "OK" if bootstrap_exit == 0 else "FAIL"
        )

        search_index_exit = self.run_streaming(
            [
                docker_exe,
                "compose",
                "exec",
                "-T",
                "api",
                "python",
                "scripts/rebuild_search_index.py",
                "--all",
            ]
        )
        self.add_stage_result(
            "rebuild_search_index.py --all", "OK" if search_index_exit == 0 else "FAIL"
        )

        for url in SMOKE_URLS:
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    status = resp.status
                self.add_stage_result(
                    f"smoke: {url}", "OK" if status == 200 else "FAIL", f"HTTP {status}"
                )
            except Exception as exc:
                self.add_stage_result(f"smoke: {url}", "FAIL", str(exc))

        if self.skip_e2e:
            self.add_stage_result(
                "pnpm web:mvp:check (Playwright E2E)", "SKIP", "--skip-e2e was set"
            )
            return

        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "node.exe"], capture_output=True)

        pnpm_exe = shutil.which("pnpm")
        self.run_gate_step(
            "pnpm web:mvp:check (Playwright E2E)",
            [pnpm_exe, "web:mvp:check"] if pnpm_exe else None,
        )

    def phase_precommit(self) -> None:
        if self.skip_precommit:
            self.add_stage_result(
                "pre-commit run --all-files", "SKIP", "--skip-precommit was set"
            )
            return
        self.section("Phase 6 — pre-commit")
        args = (
            [*self.python312, "-m", "pre_commit", "run", "--all-files"]
            if self.python312
            else None
        )
        self.run_gate_step("pre-commit run --all-files", args)

    def phase_git_status(self) -> None:
        self.section("Phase 7 — git status")
        git_exe = shutil.which("git")
        if git_exe:
            self.run_streaming([git_exe, "diff", "--check"])
            self.run_streaming([git_exe, "status", "--short"])

    def write_reports(self, finished_at: datetime) -> int:
        duration_minutes = round(
            (finished_at - self.started_at).total_seconds() / 60, 1
        )

        self.section("Summary")
        name_width = max((len(r.stage) for r in self.stage_results), default=10) + 2
        for r in self.stage_results:
            duration_text = (
                f" ({r.duration_seconds}s)" if r.duration_seconds >= 1 else ""
            )
            self.log(
                f"  [{r.status:<4}] {r.stage:<{name_width}} {r.detail}{duration_text}"
            )

        ok_count = sum(1 for r in self.stage_results if r.status == "OK")
        warn_count = sum(1 for r in self.stage_results if r.status == "WARN")
        fail_count = sum(1 for r in self.stage_results if r.status == "FAIL")
        skip_count = sum(1 for r in self.stage_results if r.status == "SKIP")

        self.log("")
        self.log(
            f"OK: {ok_count}   WARN: {warn_count}   FAIL: {fail_count}   SKIP: {skip_count}   "
            f"Duration: {duration_minutes} min"
        )

        if self.recommendations:
            self.section("Recommendations")
            rec_lines = [
                "Country Decision Atlas — full-check.py recommendations",
                f"Generated: {finished_at.isoformat()}",
                "",
            ]
            for rec in self.recommendations:
                line = f"- {rec.tool}: {rec.issue}"
                self.log(line, "warn")
                rec_lines.append(line)
                if rec.hint:
                    hint_line = f"    -> {rec.hint}"
                    self.log(hint_line, "warn")
                    rec_lines.append(hint_line)
            try:
                self.recommendations_path.write_text(
                    "\n".join(rec_lines) + "\n", encoding="utf-8"
                )
            except OSError as exc:
                self.log(f"WARNING: could not write recommendations.txt: {exc}", "warn")

        summary_lines = [
            "Country Decision Atlas — full-check.py run",
            f"Started:  {self.started_at.isoformat()}",
            f"Finished: {finished_at.isoformat()}",
            f"Duration: {duration_minutes} minutes",
            f"OK={ok_count} WARN={warn_count} FAIL={fail_count} SKIP={skip_count}",
            f"git: branch={self.git_context.get('branch')} commit={self.git_context.get('commit')} "
            f"dirty={self.git_context.get('dirty_file_count')} {self.git_context.get('ahead_behind')}",
            "",
        ]
        for r in self.stage_results:
            duration_text = (
                f" ({r.duration_seconds}s)" if r.duration_seconds >= 1 else ""
            )
            summary_lines.append(f"[{r.status}] {r.stage} {r.detail}{duration_text}")
        if self.recommendations:
            summary_lines.append("")
            summary_lines.append(
                f"See recommendations.txt for {len(self.recommendations)} actionable suggestion(s)."
            )
        try:
            self.summary_path.write_text(
                "\n".join(summary_lines) + "\n", encoding="utf-8"
            )
        except OSError as exc:
            self.log(f"WARNING: could not write summary.txt: {exc}", "warn")

        try:
            report = {
                "started_at": self.started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "duration_minutes": duration_minutes,
                "counts": {
                    "ok": ok_count,
                    "warn": warn_count,
                    "fail": fail_count,
                    "skip": skip_count,
                },
                "git": self.git_context,
                "system": self.system_info,
                "network": [asdict(n) for n in self.network_results],
                "stages": [asdict(s) for s in self.stage_results],
                "recommendations": [asdict(r) for r in self.recommendations],
            }
            self.report_json_path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except OSError as exc:
            self.log(f"WARNING: could not write report.json: {exc}", "warn")

        self.log("")
        self.log(f"Full transcript:  {self.transcript_path}")
        self.log(f"Summary:          {self.summary_path}")
        self.log(f"JSON report:      {self.report_json_path}")
        if self.recommendations:
            self.log(f"Recommendations:  {self.recommendations_path}")

        return fail_count

    def run(self) -> int:
        self.section("Country Decision Atlas — full local check")
        self.log(f"Report folder: {self.report_dir}")
        self.log(f"Started at:    {self.started_at}")

        config = self.load_config()

        fail_count = 0
        try:
            self.phase_diagnostics(config)
            self.phase_toolchain(config)
            self.phase_dependencies()
            self.phase_pinned_versions()
            self.phase_static_quality()
            self.phase_go_notifier()
            self.phase_docker()
            self.phase_precommit()
            self.phase_git_status()
        except Exception as exc:
            self.add_stage_result("UNEXPECTED SCRIPT ERROR", "FAIL", str(exc))
            self.log("")
            self.log(
                "An unexpected error occurred. The script did not crash — see the report for details.",
                "error",
            )
        finally:
            fail_count = self.write_reports(datetime.now())
            self.out.close()

        return 1 if fail_count > 0 else 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Country Decision Atlas — full local check"
    )
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-e2e", action="store_true")
    parser.add_argument("--skip-precommit", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--docker-max-attempts", type=int, default=5)
    parser.add_argument("--docker-retry-initial-delay", type=int, default=5)
    parser.add_argument("--docker-retry-delay-step", type=int, default=2)
    parser.add_argument("--admin-token", default="")
    parser.add_argument("--config", default="")
    parser.add_argument("--regen-proto", action="store_true", default=False)
    return parser.parse_args(argv)


def make_console_encoding_safe() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            with contextlib.suppress(ValueError):
                reconfigure(errors="replace")


def main(argv: list[str] | None = None) -> int:
    make_console_encoding_safe()
    args = parse_args(argv)
    checker = FullCheck(args)
    return checker.run()


if __name__ == "__main__":
    sys.exit(main())
