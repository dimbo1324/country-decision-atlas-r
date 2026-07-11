from __future__ import annotations

import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts" / "dev_tools"

Lang = str  # "en" or "ru"
DEFAULT_LANG: Lang = "en"


@dataclass(frozen=True)
class Text:
    """A short piece of UI copy in both supported languages. English is
    the interface default; Russian is always available on request
    (`L`/`lang` in interactive mode, `--lang ru` for the `help` command)."""

    en: str
    ru: str

    def get(self, lang: Lang) -> str:
        return self.ru if lang == "ru" else self.en


@dataclass(frozen=True)
class Category:
    key: str
    title: Text
    blurb: Text


@dataclass(frozen=True)
class ScriptInfo:
    title: str
    filename: str
    category: str
    summary: Text
    description: Text
    cadence: Text
    aliases: tuple[str, ...] = ()
    directory: Path = SCRIPTS_DIR
    examples: tuple[str, ...] = ()

    @property
    def identifiers(self) -> frozenset[str]:
        return frozenset(
            {self.title.lower(), self.filename.lower(), *self.aliases}
        )


# Categories group scripts by the task they perform, so the interactive menu
# stays readable as the registry grows — add a category here only when an
# existing one genuinely doesn't fit; otherwise add the script to one that
# already exists.
CATEGORIES: list[Category] = [
    Category(
        key="quality",
        title=Text(
            en="Quality Gate & Formatting",
            ru="Контроль качества и форматирование",
        ),
        blurb=Text(
            en="Run checks and auto-format code before you commit or push.",
            ru="Проверки и автоформатирование перед коммитом и пушем.",
        ),
    ),
    Category(
        key="release",
        title=Text(en="Git & Release", ru="Git и релиз"),
        blurb=Text(
            en="Ship already-reviewed work to main.",
            ru="Публикация уже проверенных изменений в main.",
        ),
    ),
    Category(
        key="jobs",
        title=Text(en="Scheduled Data Jobs", ru="Плановые джобы данных"),
        blurb=Text(
            en="Recurring background jobs (outbox relay, retention, reminders) — cron/systemd once deployed.",
            ru="Регулярные фоновые джобы (relay, retention, напоминания) — cron/systemd после выбора деплой-цели.",
        ),
    ),
    Category(
        key="backup",
        title=Text(
            en="Backups & Recovery", ru="Резервное копирование и восстановление"
        ),
        blurb=Text(
            en="Postgres backups and periodic restore-integrity checks.",
            ru="Бэкапы Postgres и периодическая проверка целостности восстановления.",
        ),
    ),
    Category(
        key="recompute",
        title=Text(
            en="Recompute Derived Data", ru="Пересчёт производных данных"
        ),
        blurb=Text(
            en="Manually re-trigger derived metrics normally enqueued from admin endpoints.",
            ru="Ручной перезапуск пересчёта производных метрик, которые обычно ставятся в очередь из admin-эндпоинтов.",
        ),
    ),
    Category(
        key="demo",
        title=Text(en="Demo Dataset Management", ru="Управление демо-набором"),
        blurb=Text(
            en="Restore or export the conserved demo countries (russia, uruguay, argentina).",
            ru="Восстановление или экспорт консервированного демо-набора стран (russia, uruguay, argentina).",
        ),
    ),
    Category(
        key="assistant",
        title=Text(en="AI Assistant Config", ru="Конфигурация AI-ассистентов"),
        blurb=Text(
            en="Keep AGENTS.md in sync with the shared .ai/ rule modules.",
            ru="Синхронизация AGENTS.md с общими модулями правил .ai/.",
        ),
    ),
    Category(
        key="reports",
        title=Text(en="Reports & Diagnostics", ru="Отчёты и диагностика"),
        blurb=Text(
            en="Read-only status reports; nothing here changes data.",
            ru="Отчёты только для чтения; ничего не изменяет данные.",
        ),
    ),
]

_RECURRING_JOB_CADENCE = Text(
    en=(
        "Recurring — intended for cron/systemd timer/CronJob once a "
        "deployment target exists; run manually until then."
    ),
    ru=(
        "Регулярно — предназначен для cron/systemd timer/CronJob после "
        "выбора деплой-цели; до этого запускается вручную."
    ),
)
_RECOMPUTE_CADENCE = Text(
    en=(
        "On-demand — the manual/CLI counterpart to the async recompute "
        "an admin endpoint enqueues."
    ),
    ru=(
        "По требованию — ручной/CLI аналог асинхронного пересчёта, "
        "который admin-эндпоинт ставит в очередь."
    ),
)

# Add new scripts here as they're placed in scripts/dev_tools/ (default
# directory) or elsewhere under scripts/ (set directory= explicitly). Give
# every script a `category` matching one of CATEGORIES above — that's the
# only structural requirement for the menu to pick it up correctly.
AVAILABLE_SCRIPTS: list[ScriptInfo] = [
    ScriptInfo(
        title="full-check",
        filename="full_check.py",
        category="quality",
        summary=Text(
            en="Run the local quality gate: lint, types, tests, optional Docker/E2E.",
            ru="Локальный quality gate: линт, типы, тесты, опционально Docker/E2E.",
        ),
        description=Text(
            en=(
                "Runs the local quality gate: toolchain checks, dependency "
                "install, static analysis (ruff/mypy/sqlfluff), pytest "
                "(including scripts/synthetic_data), and — on fuller "
                "profiles — the Docker stack, migrations, runtime smokes, "
                "and Playwright E2E. Accepts full_check.py's own flags "
                "unchanged: --profile {quick,backend,frontend,full,ci}, "
                "--fix, --doctor. This is the default script: running the "
                "orchestrator with no arguments (non-interactively) runs it "
                "directly."
            ),
            ru=(
                "Запускает локальный quality gate: проверка тулчейна, "
                "установка зависимостей, статический анализ "
                "(ruff/mypy/sqlfluff), pytest (включая "
                "scripts/synthetic_data), а на более полных профилях — "
                "Docker-стек, миграции, runtime-смоки и Playwright E2E. "
                "Принимает собственные флаги full_check.py без изменений: "
                "--profile {quick,backend,frontend,full,ci}, --fix, "
                "--doctor. Это скрипт по умолчанию: запуск оркестратора "
                "без аргументов (не в интерактивном режиме) выполняет "
                "именно его."
            ),
        ),
        cadence=Text(
            en="Run before every merge; --profile quick is the minimum before every push.",
            ru="Запускать перед каждым мерджем; --profile quick — минимум перед каждым push.",
        ),
        aliases=("check", "quality"),
        examples=("--profile quick", "--profile full", "--doctor", "--fix"),
    ),
    ScriptInfo(
        title="format-code",
        filename="format_code.py",
        category="quality",
        summary=Text(
            en="Auto-format Python, frontend/contracts, and Go code.",
            ru="Автоформатирование Python, frontend/contracts и Go.",
        ),
        description=Text(
            en=(
                "Runs ruff format (Python), prettier (frontend + "
                "contracts), and gofmt (Go notifier) in one pass. Accepts "
                "an optional positional target: python, frontend, go, or "
                "all (default)."
            ),
            ru=(
                "Запускает ruff format (Python), prettier (frontend + "
                "contracts) и gofmt (Go notifier) за один проход. Принимает "
                "необязательный позиционный аргумент: python, frontend, go "
                "или all (по умолчанию)."
            ),
        ),
        cadence=Text(
            en="On-demand, whenever code needs reformatting.",
            ru="По требованию, когда нужно переформатировать код.",
        ),
        aliases=("format", "fmt"),
        examples=("", "python", "frontend", "go"),
    ),
    ScriptInfo(
        title="ship-main",
        filename="ship_main.py",
        category="release",
        summary=Text(
            en="Format, commit, quick-gate, fast-forward, and push main.",
            ru="Форматирование, коммит, quick-gate, fast-forward и push в main.",
        ),
        description=Text(
            en=(
                "A guided, opinionated publish flow: formats code, commits "
                "with the given message, runs the quick quality gate, "
                "fast-forwards local main from origin/main, and pushes. "
                'Requires --message "type: why". Intended only for '
                "already-reviewed, ready-to-ship work — it does not "
                "replace the branch → gate → merge workflow for feature "
                "work."
            ),
            ru=(
                "Управляемый сценарий публикации с фиксированными шагами: "
                "форматирует код, коммитит с указанным сообщением, "
                "прогоняет quick quality gate, делает fast-forward "
                "локального main от origin/main и пушит. Требует --message "
                '"type: почему". Предназначен только для уже проверенной, '
                "готовой к выпуску работы — не заменяет обычный цикл "
                "branch → gate → merge для фич."
            ),
        ),
        cadence=Text(
            en="On-demand, only for already-reviewed, ready-to-ship work.",
            ru="По требованию, только для уже проверенной, готовой к выпуску работы.",
        ),
        aliases=("ship", "push-main", "publish"),
        examples=('--message "docs: update notes"',),
    ),
    ScriptInfo(
        title="dispatch-trip-reminders",
        filename="dispatch_trip_reminders.py",
        category="jobs",
        summary=Text(
            en="Dispatch due trip reminders into the domain_events outbox.",
            ru="Отправка назревших напоминаний о поездках в outbox domain_events.",
        ),
        description=Text(
            en=(
                "Dispatches due trip reminders into the domain_events "
                "outbox (transactional, idempotent, SKIP LOCKED — safe to "
                "run concurrently or re-run after a crash). Accepts "
                "--limit and --dry-run."
            ),
            ru=(
                "Отправляет назревшие напоминания о поездках в outbox "
                "domain_events (транзакционно, идемпотентно, SKIP LOCKED "
                "— безопасно запускать параллельно или повторно после "
                "сбоя). Принимает --limit и --dry-run."
            ),
        ),
        cadence=_RECURRING_JOB_CADENCE,
        aliases=("dispatch-reminders", "trip-reminders"),
        directory=ROOT_DIR / "scripts",
        examples=("--dry-run", "--limit 100"),
    ),
    ScriptInfo(
        title="cleanup-retention",
        filename="cleanup_retention.py",
        category="jobs",
        summary=Text(
            en="Delete rows past their configured retention window.",
            ru="Удаление строк, вышедших за окно хранения (retention).",
        ),
        description=Text(
            en=(
                "Deletes rows past their configured retention window from "
                "analytics_events, ai_interaction_logs, relayed "
                "domain_events, and expired/revoked auth_sessions. "
                "Windows come from methodology_config.py, not hardcoded "
                "here. Accepts --dry-run."
            ),
            ru=(
                "Удаляет строки, вышедшие за настроенное окно хранения, из "
                "analytics_events, ai_interaction_logs, доставленных "
                "domain_events и истёкших/отозванных auth_sessions. Окна "
                "хранения берутся из methodology_config.py, а не заданы в "
                "этом скрипте. Принимает --dry-run."
            ),
        ),
        cadence=_RECURRING_JOB_CADENCE,
        aliases=("retention-cleanup", "cleanup-retention.py"),
        directory=ROOT_DIR / "scripts",
        examples=("--dry-run",),
    ),
    ScriptInfo(
        title="cleanup-expired-sessions",
        filename="cleanup_expired_auth_sessions.py",
        category="jobs",
        summary=Text(
            en="Mark expired auth sessions as revoked.",
            ru="Пометка истёкших сессий как отозванных.",
        ),
        description=Text(
            en=(
                "Marks expired-but-not-yet-revoked auth_sessions as "
                "revoked (sets revoked_at). Complements cleanup-retention, "
                "which only deletes rows already past the retention "
                "window — this keeps the session listing/audit trail "
                "accurate in the meantime. Accepts --limit and --dry-run."
            ),
            ru=(
                "Помечает истёкшие, но ещё не отозванные auth_sessions как "
                "отозванные (устанавливает revoked_at). Дополняет "
                "cleanup-retention, которая удаляет только строки, уже "
                "вышедшие за окно хранения — это поддерживает точность "
                "списка сессий/аудита между удалениями. Принимает --limit "
                "и --dry-run."
            ),
        ),
        cadence=_RECURRING_JOB_CADENCE,
        aliases=("cleanup-sessions", "expired-sessions"),
        directory=ROOT_DIR / "scripts",
        examples=("--dry-run", "--limit 200"),
    ),
    ScriptInfo(
        title="outbox-relay",
        filename="outbox_relay.py",
        category="jobs",
        summary=Text(
            en="Relay pending domain_events to Kafka.",
            ru="Доставка ожидающих domain_events в Kafka.",
        ),
        description=Text(
            en=(
                "Relays pending domain_events to Kafka using a short claim "
                "transaction, a publish step outside that transaction, and "
                "a short result transaction (P1-1, Аудит-эпизод 4) — so a "
                "Kafka outage never holds a long-lived DB transaction "
                "open. Reads DATABASE_URL/KAFKA_BROKERS/KAFKA_TOPIC "
                "directly from the environment, not from Settings. Accepts "
                "--batch-size, --max-attempts, --notify-after, --dry-run, "
                "--metrics-json, --metrics-output."
            ),
            ru=(
                "Доставляет ожидающие domain_events в Kafka: короткая "
                "транзакция захвата, публикация вне транзакции, короткая "
                "транзакция фиксации результата (P1-1, Аудит-эпизод 4) — "
                "сбой Kafka никогда не держит открытой долгую транзакцию "
                "БД. Читает DATABASE_URL/KAFKA_BROKERS/KAFKA_TOPIC "
                "напрямую из окружения, а не из Settings. Принимает "
                "--batch-size, --max-attempts, --notify-after, --dry-run, "
                "--metrics-json, --metrics-output."
            ),
        ),
        cadence=_RECURRING_JOB_CADENCE,
        aliases=("relay", "domain-events-relay"),
        directory=ROOT_DIR / "scripts",
        examples=("--dry-run", "--batch-size 50 --max-attempts 5"),
    ),
    ScriptInfo(
        title="backup-postgres",
        filename="backup_postgres.py",
        category="backup",
        summary=Text(
            en="Dump the running Postgres service to a timestamped file.",
            ru="Дамп текущего сервиса Postgres в файл с меткой времени.",
        ),
        description=Text(
            en=(
                "Runs pg_dump against the running postgres service via "
                "`docker compose exec` and writes a timestamped .sql file "
                "to backups/postgres/. Accepts --output-dir, --service, "
                "and --dry-run."
            ),
            ru=(
                "Запускает pg_dump для работающего сервиса postgres через "
                "`docker compose exec` и записывает .sql-файл с меткой "
                "времени в backups/postgres/. Принимает --output-dir, "
                "--service и --dry-run."
            ),
        ),
        cadence=_RECURRING_JOB_CADENCE,
        aliases=("backup-db", "pg-backup"),
        directory=ROOT_DIR / "scripts",
        examples=(
            "--dry-run",
            "--output-dir backups/postgres --service postgres",
        ),
    ),
    ScriptInfo(
        title="restore-postgres-check",
        filename="restore_postgres_check.py",
        category="backup",
        summary=Text(
            en="Verify a backup restores cleanly in a scratch container.",
            ru="Проверка, что бэкап восстанавливается в одноразовом контейнере.",
        ),
        description=Text(
            en=(
                "Restores a pg_dump backup into a disposable scratch "
                "Postgres container (never the real database), verifies "
                "schema_migrations is populated, then discards the "
                "container. Requires --backup-file. Accepts --dry-run."
            ),
            ru=(
                "Восстанавливает pg_dump-бэкап в одноразовом "
                "scratch-контейнере Postgres (никогда не в боевой базе), "
                "проверяет, что schema_migrations заполнена, затем удаляет "
                "контейнер. Требует --backup-file. Принимает --dry-run."
            ),
        ),
        cadence=Text(
            en="Periodic backup-integrity check — run regularly against your latest backup.",
            ru="Периодическая проверка целостности бэкапа — запускать регулярно на последнем бэкапе.",
        ),
        aliases=("restore-check", "pg-restore-check"),
        directory=ROOT_DIR / "scripts",
        examples=("--backup-file backups/postgres/2026-07-11.sql --dry-run",),
    ),
    ScriptInfo(
        title="recompute-author-reputation",
        filename="recompute_author_reputation.py",
        category="recompute",
        summary=Text(
            en="Recompute derived author reputation scores.",
            ru="Пересчёт производной репутации автора.",
        ),
        description=Text(
            en=(
                "Recomputes derived author reputation (coverage/freshness/"
                "sourcing scores, subscriber and published-metric counts) "
                "for one author or all authors with published metrics. "
                "Accepts --all or --author, and --dry-run."
            ),
            ru=(
                "Пересчитывает производную репутацию автора (оценки "
                "coverage/freshness/sourcing, число подписчиков и "
                "опубликованных метрик) для одного автора или всех "
                "авторов с опубликованными метриками. Принимает --all или "
                "--author, и --dry-run."
            ),
        ),
        cadence=_RECOMPUTE_CADENCE,
        aliases=("author-reputation", "recompute-reputation"),
        directory=ROOT_DIR / "scripts",
        examples=("--all --dry-run", "--author <author_id>"),
    ),
    ScriptInfo(
        title="recompute-country-drift",
        filename="recompute_country_drift.py",
        category="recompute",
        summary=Text(
            en="Recompute country drift snapshots.",
            ru="Пересчёт снапшотов дрейфа страны.",
        ),
        description=Text(
            en=(
                "Recomputes country drift snapshots for one country or "
                "all active countries. Accepts --all or --country, "
                "--dry-run, and --no-events. The idempotent single-"
                "country path for the 'recompute all' admin endpoint, "
                "which only enqueues a request rather than looping "
                "synchronously (P2-3, Аудит-эпизод 5)."
            ),
            ru=(
                "Пересчитывает снапшоты дрейфа для одной страны или всех "
                "активных стран. Принимает --all или --country, --dry-run "
                "и --no-events. Идемпотентный путь для одной страны, "
                "лежащий в основе admin-эндпоинта «пересчитать всё», "
                "который только ставит запрос в очередь, а не выполняет "
                "синхронный цикл (P2-3, Аудит-эпизод 5)."
            ),
        ),
        cadence=_RECOMPUTE_CADENCE,
        aliases=("recompute-drift", "country-drift"),
        directory=ROOT_DIR / "scripts",
        examples=("--all --dry-run", "--country argentina"),
    ),
    ScriptInfo(
        title="recompute-platform-metrics",
        filename="recompute_platform_metrics.py",
        category="recompute",
        summary=Text(
            en="Recompute platform intelligence metrics.",
            ru="Пересчёт метрик platform intelligence.",
        ),
        description=Text(
            en=(
                "Recomputes platform intelligence metrics for one country "
                "or all active countries. Accepts --all or --country, "
                "--dry-run, --metric-key, and --scenario-slug. Same "
                "enqueue-not-loop relationship to its admin HTTP endpoint "
                "as recompute-country-drift (P2-3, Аудит-эпизод 5)."
            ),
            ru=(
                "Пересчитывает метрики platform intelligence для одной "
                "страны или всех активных стран. Принимает --all или "
                "--country, --dry-run, --metric-key и --scenario-slug. Та "
                "же связь «постановка в очередь, а не цикл» с admin "
                "HTTP-эндпоинтом, что и у recompute-country-drift (P2-3, "
                "Аудит-эпизод 5)."
            ),
        ),
        cadence=_RECOMPUTE_CADENCE,
        aliases=("recompute-metrics", "platform-metrics"),
        directory=ROOT_DIR / "scripts",
        examples=(
            "--all --dry-run",
            "--country argentina --metric-key cost_of_living",
        ),
    ),
    ScriptInfo(
        title="recompute-trust-scores",
        filename="recompute_trust_scores.py",
        category="recompute",
        summary=Text(
            en="Recompute country trust scores.",
            ru="Пересчёт trust-скоров страны.",
        ),
        description=Text(
            en=(
                "Recomputes country trust scores for one country or all "
                "active countries. Accepts --all or --country and "
                "--dry-run. Same enqueue-not-loop relationship to its "
                "admin HTTP endpoint as recompute-country-drift (P2-3, "
                "Аудит-эпизод 5)."
            ),
            ru=(
                "Пересчитывает trust-скоры для одной страны или всех "
                "активных стран. Принимает --all или --country и "
                "--dry-run. Та же связь «постановка в очередь, а не цикл» "
                "с admin HTTP-эндпоинтом, что и у recompute-country-drift "
                "(P2-3, Аудит-эпизод 5)."
            ),
        ),
        cadence=_RECOMPUTE_CADENCE,
        aliases=("recompute-trust", "trust-scores"),
        directory=ROOT_DIR / "scripts",
        examples=("--all --dry-run", "--country russia"),
    ),
    ScriptInfo(
        title="restore-demo-countries",
        filename="restore_demo_countries.py",
        category="demo",
        summary=Text(
            en="Restore the conserved demo countries from fixtures.",
            ru="Восстановление консервированных демо-стран из фикстур.",
        ),
        description=Text(
            en=(
                "Idempotently restores the conserved demo country dataset "
                "(russia, uruguay, argentina) from "
                "database/fixtures/demo_countries/ JSON fixtures. Accepts "
                "--dry-run. --visible additionally lifts is_demo for the "
                "restored rows (used by CI/E2E jobs only — see "
                "docs/_arch_/08_Открытые_вопросы.md, Р-11)."
            ),
            ru=(
                "Идемпотентно восстанавливает консервированный демо-набор "
                "стран (russia, uruguay, argentina) из JSON-фикстур в "
                "database/fixtures/demo_countries/. Принимает --dry-run. "
                "--visible дополнительно снимает is_demo для "
                "восстановленных строк (используется только CI/E2E-"
                "джобами — см. docs/_arch_/08_Открытые_вопросы.md, Р-11)."
            ),
        ),
        cadence=Text(
            en="On-demand — whenever the local demo dataset needs restoring.",
            ru="По требованию — когда нужно восстановить локальный демо-набор.",
        ),
        aliases=("restore-demo", "demo-countries"),
        examples=("--dry-run", "--visible"),
    ),
    ScriptInfo(
        title="export-demo-countries",
        filename="export_demo_countries.py",
        category="demo",
        summary=Text(
            en="Export the conserved demo countries to fixtures.",
            ru="Экспорт консервированных демо-стран в фикстуры.",
        ),
        description=Text(
            en=(
                "Exports the conserved demo country dataset (russia, "
                "uruguay, argentina) to JSON fixtures under "
                "database/fixtures/demo_countries/ — the inverse of "
                "restore-demo-countries. Takes no flags. Run this after a "
                "deliberate change to the demo dataset, then commit the "
                "updated fixtures."
            ),
            ru=(
                "Экспортирует консервированный демо-набор стран (russia, "
                "uruguay, argentina) в JSON-фикстуры в "
                "database/fixtures/demo_countries/ — операция, обратная "
                "restore-demo-countries. Не принимает флагов. Запускайте "
                "после осознанного изменения демо-набора, затем "
                "закоммитьте обновлённые фикстуры."
            ),
        ),
        cadence=Text(
            en="On-demand — only after a deliberate change to the demo dataset.",
            ru="По требованию — только после осознанного изменения демо-набора.",
        ),
        aliases=("export-demo",),
    ),
    ScriptInfo(
        title="sync-agents",
        filename="sync_agents_md.py",
        category="assistant",
        summary=Text(
            en="Regenerate AGENTS.md from the shared .ai/ rule modules.",
            ru="Регенерация AGENTS.md из общих модулей правил .ai/.",
        ),
        description=Text(
            en=(
                "Regenerates AGENTS.md from the shared AI-assistant rule "
                "modules in .ai/ (universal + project) — the single "
                "source of truth for both Claude Code and Codex. Never "
                "hand-edit AGENTS.md; edit a module and re-run this. Pass "
                "--check to verify AGENTS.md is in sync without writing "
                "(used by CI)."
            ),
            ru=(
                "Регенерирует AGENTS.md из общих модулей правил "
                "ассистентов в .ai/ (universal + project) — единственный "
                "источник истины для Claude Code и Codex. Никогда не "
                "редактируйте AGENTS.md вручную — меняйте модуль и "
                "перезапускайте эту команду. Флаг --check проверяет "
                "синхронизацию AGENTS.md без записи (используется в CI)."
            ),
        ),
        cadence=Text(
            en="On-demand — every time a .ai/ rule module changes.",
            ru="По требованию — при каждом изменении модуля правил в .ai/.",
        ),
        aliases=("sync-agents-md", "agents-sync"),
        examples=("--check",),
    ),
    ScriptInfo(
        title="translation-pipeline-status",
        filename="translation_pipeline_status.py",
        category="reports",
        summary=Text(
            en="Read-only report on translation units and jobs.",
            ru="Отчёт только для чтения о юнитах и джобах перевода.",
        ),
        description=Text(
            en=(
                "Read-only report: translation units and jobs by status, "
                "and counts of missing/stale EN translations. Takes no "
                "flags and never modifies data — safe to run at any time."
            ),
            ru=(
                "Отчёт только для чтения: юниты и джобы перевода по "
                "статусам, количество отсутствующих/устаревших переводов "
                "на EN. Не принимает флагов и никогда не изменяет данные "
                "— безопасно запускать в любой момент."
            ),
        ),
        cadence=Text(
            en="On-demand, read-only — safe to run anytime.",
            ru="По требованию, только для чтения — безопасно запускать в любой момент.",
        ),
        aliases=("translation-status", "i18n-status"),
        directory=ROOT_DIR / "scripts",
    ),
]

DEFAULT_SCRIPT_TITLE = "full-check"


@dataclass
class Session:
    """Mutable per-run interactive state — currently just the display
    language, threaded through the top menu, category submenus, and the
    help browser so a language switch anywhere sticks for the rest of the
    session."""

    lang: Lang = DEFAULT_LANG

    def toggle_lang(self) -> None:
        self.lang = "ru" if self.lang == "en" else "en"


def find_script(choice: str) -> ScriptInfo | None:
    normalized = choice.strip().lower()
    for script in AVAILABLE_SCRIPTS:
        if normalized in script.identifiers:
            return script
    return None


def find_category(choice: str) -> Category | None:
    normalized = choice.strip().lower()
    for category in CATEGORIES:
        names = {
            category.key,
            category.title.en.lower(),
            category.title.ru.lower(),
        }
        if normalized in names:
            return category
    return None


def scripts_in(category_key: str) -> list[ScriptInfo]:
    return [
        script
        for script in AVAILABLE_SCRIPTS
        if script.category == category_key
    ]


def default_script() -> ScriptInfo:
    script = find_script(DEFAULT_SCRIPT_TITLE)
    assert script is not None, (
        "DEFAULT_SCRIPT_TITLE must match a registered script"
    )
    return script


def _stdin_is_interactive() -> bool:
    try:
        return sys.stdin.isatty()
    except (AttributeError, ValueError):
        return False


def _unknown_choice_message(raw_choice: str, lang: Lang) -> str:
    if lang == "ru":
        return f"\nНеизвестный выбор: {raw_choice!r}. Попробуйте снова.\n"
    return f"\nUnknown choice: {raw_choice!r}. Try again.\n"


# ____________________________________________________________________________
#                               Rendering
# ____________________________________________________________________________


def print_top_menu(lang: Lang) -> None:
    heading = (
        "Country Decision Atlas — script orchestrator"
        if lang == "en"
        else "Country Decision Atlas — оркестратор скриптов"
    )
    print(f"\n{heading}")
    print("=" * len(heading))
    print(
        "Pick a category, or type a script's name to jump straight to it. "
        "Press Enter for the default full quality gate.\n"
        if lang == "en"
        else "Выберите категорию или введите имя скрипта, чтобы перейти к "
        "нему напрямую. Enter — quality gate по умолчанию.\n"
    )

    for index, category in enumerate(CATEGORIES, start=1):
        count = len(scripts_in(category.key))
        print(f"{index}. {category.title.get(lang)} ({count})")
        print(f"   {category.blurb.get(lang)}")

    print()
    if lang == "en":
        print("H. Help — detailed manual for any script")
        print("L. Language: English — switch to Russian")
        print("Q. Quit")
    else:
        print("H. Help — подробное описание любого скрипта")
        print("L. Язык: русский — переключить на английский")
        print("Q. Выход")


def _top_prompt(lang: Lang) -> str:
    if lang == "en":
        return f"\nYour choice [default: {DEFAULT_SCRIPT_TITLE}]: "
    return f"\nВаш выбор [по умолчанию: {DEFAULT_SCRIPT_TITLE}]: "


def print_category_menu(
    category: Category, scripts: list[ScriptInfo], lang: Lang
) -> None:
    heading = category.title.get(lang)
    print(f"\n{heading}")
    print("=" * len(heading))
    for index, script in enumerate(scripts, start=1):
        default_marker = (
            " [default]" if script.title == DEFAULT_SCRIPT_TITLE else ""
        )
        print(f"{index}. {script.title}{default_marker}")
        print(f"   {script.summary.get(lang)}")
        if script.aliases:
            label = "aliases" if lang == "en" else "алиасы"
            print(f"   {label}: {', '.join(script.aliases)}")

    print()
    if lang == "en":
        print("B. Back   H. Help   L. Language   Q. Quit")
    else:
        print("B. Назад   H. Справка   L. Язык   Q. Выход")


def _category_prompt(lang: Lang) -> str:
    return "\nYour choice: " if lang == "en" else "\nВаш выбор: "


def print_help_catalog(lang: Lang) -> None:
    heading = "Script manual" if lang == "en" else "Справочник по скриптам"
    print(f"\n{heading}")
    print("=" * len(heading))

    number = 1
    for category in CATEGORIES:
        entries = scripts_in(category.key)
        if not entries:
            continue
        print(f"\n{category.title.get(lang)}")
        for script in entries:
            print(
                f"  {number:>2}. {script.title:<28} {script.summary.get(lang)}"
            )
            number += 1

    print(
        "\nType a number or script name for its full manual; B to go back."
        if lang == "en"
        else "\nВведите номер или имя скрипта для полного описания; B — назад."
    )


def _help_prompt(lang: Lang) -> str:
    return "\nYour choice: " if lang == "en" else "\nВаш выбор: "


def print_manual(script: ScriptInfo, lang: Lang) -> None:
    print(f"\n{script.title}")
    print("-" * len(script.title))

    category = next(c for c in CATEGORIES if c.key == script.category)
    relative_path = (script.directory / script.filename).relative_to(ROOT_DIR)

    if lang == "en":
        print(f"Category: {category.title.en}")
        if script.aliases:
            print(f"Aliases:  {', '.join(script.aliases)}")
        print(f"Path:     {relative_path}")
        print(f"Cadence:  {script.cadence.en}")
        print(f"\n{script.description.en}")
        if script.examples:
            print("\nExamples:")
    else:
        print(f"Категория:     {category.title.ru}")
        if script.aliases:
            print(f"Алиасы:        {', '.join(script.aliases)}")
        print(f"Путь:          {relative_path}")
        print(f"Периодичность: {script.cadence.ru}")
        print(f"\n{script.description.ru}")
        if script.examples:
            print("\nПримеры:")

    for example in script.examples:
        command = f"python dev_tools_scripts_runner.py {script.title} {example}"
        print(f"  {command.rstrip()}")


# ____________________________________________________________________________
#                               Execution
# ____________________________________________________________________________


def run_script(script: ScriptInfo, extra_args: list[str]) -> int:
    script_path = script.directory / script.filename

    if not script_path.exists():
        print(f"ERROR: script file not found: {script_path}", file=sys.stderr)
        return 1

    completed_process = subprocess.run(
        [sys.executable, str(script_path), *extra_args],
        cwd=ROOT_DIR,
        check=False,
    )
    return completed_process.returncode


def _prompt_extra_args(script: ScriptInfo, lang: Lang) -> list[str]:
    prompt = (
        f"Extra arguments for {script.title} (optional, Enter to skip): "
        if lang == "en"
        else f"Дополнительные аргументы для {script.title} "
        "(необязательно, Enter — пропустить): "
    )
    raw = input(prompt).strip()
    return shlex.split(raw) if raw else []


def _launch(script: ScriptInfo, lang: Lang) -> int:
    return run_script(script, _prompt_extra_args(script, lang))


def _run_help_browser(session: Session) -> None:
    while True:
        print_help_catalog(session.lang)
        raw_choice = input(_help_prompt(session.lang)).strip()
        lowered = raw_choice.lower()

        if not raw_choice or lowered in ("b", "back", "назад"):
            return
        if lowered in ("l", "lang", "language", "язык"):
            session.toggle_lang()
            continue

        script: ScriptInfo | None = None
        if raw_choice.isdigit():
            index = int(raw_choice)
            if 1 <= index <= len(AVAILABLE_SCRIPTS):
                script = AVAILABLE_SCRIPTS[index - 1]
        if script is None:
            script = find_script(raw_choice)

        if script is None:
            print(_unknown_choice_message(raw_choice, session.lang))
            continue
        print_manual(script, session.lang)


def _run_category(category: Category, session: Session) -> int | None:
    """Returns an exit code once the user runs something or quits, or
    None to signal "go back to the top menu"."""
    scripts = scripts_in(category.key)
    while True:
        print_category_menu(category, scripts, session.lang)
        raw_choice = input(_category_prompt(session.lang)).strip()
        lowered = raw_choice.lower()

        if not raw_choice or lowered in ("b", "back", "назад"):
            return None
        if lowered in ("q", "quit", "exit", "выход"):
            return 0
        if lowered in ("l", "lang", "language", "язык"):
            session.toggle_lang()
            continue
        if lowered in ("h", "help", "справка"):
            for entry in scripts:
                print_manual(entry, session.lang)
            continue

        if raw_choice.isdigit():
            index = int(raw_choice)
            if 1 <= index <= len(scripts):
                return _launch(scripts[index - 1], session.lang)
            print(_unknown_choice_message(raw_choice, session.lang))
            continue

        script = find_script(raw_choice)
        if script is not None:
            return _launch(script, session.lang)

        print(_unknown_choice_message(raw_choice, session.lang))


def run_interactive() -> int:
    session = Session()
    while True:
        print_top_menu(session.lang)
        raw_choice = input(_top_prompt(session.lang)).strip()
        lowered = raw_choice.lower()

        if not raw_choice:
            return _launch(default_script(), session.lang)
        if lowered in ("q", "quit", "exit", "выход"):
            return 0
        if lowered in ("h", "help", "справка"):
            _run_help_browser(session)
            continue
        if lowered in ("l", "lang", "language", "язык"):
            session.toggle_lang()
            continue

        script = find_script(raw_choice)
        if script is not None:
            return _launch(script, session.lang)

        category = (
            CATEGORIES[int(raw_choice) - 1]
            if raw_choice.isdigit() and 1 <= int(raw_choice) <= len(CATEGORIES)
            else find_category(raw_choice)
        )
        if category is not None:
            outcome = _run_category(category, session)
            if outcome is not None:
                return outcome
            continue

        print(_unknown_choice_message(raw_choice, session.lang))


def _parse_help_args(rest: list[str]) -> tuple[Lang, list[str]]:
    lang: Lang = DEFAULT_LANG
    remaining: list[str] = []
    index = 0
    while index < len(rest):
        token = rest[index]
        if token == "--lang" and index + 1 < len(rest):
            lang = "ru" if rest[index + 1].lower().startswith("ru") else "en"
            index += 2
            continue
        remaining.append(token)
        index += 1
    return lang, remaining


def run_help_command(rest: list[str]) -> int:
    lang, remaining = _parse_help_args(rest)

    if not remaining:
        print_help_catalog(lang)
        return 0

    script = find_script(remaining[0])
    if script is None:
        message = (
            f"Unknown script: {remaining[0]!r}"
            if lang == "en"
            else f"Неизвестный скрипт: {remaining[0]!r}"
        )
        print(message, file=sys.stderr)
        print_help_catalog(lang)
        return 2

    print_manual(script, lang)
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0].lower() in ("help", "--help", "-h"):
        return run_help_command(argv[1:])

    if not argv:
        if _stdin_is_interactive():
            return run_interactive()
        # Non-interactive and no arguments: honor the documented behavior
        # ("full quality gate (default)") instead of blocking on input().
        return run_script(default_script(), [])

    script = find_script(argv[0])
    if script is not None:
        return run_script(script, argv[1:])

    # The first argument isn't a registered script key/name — treat the whole
    # argv as flags for the default script, so existing invocations like
    # `python dev_tools_scripts_runner.py --profile full --fix` keep working unchanged.
    return run_script(default_script(), argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
