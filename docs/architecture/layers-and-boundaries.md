# Layers and System Boundaries

> How the repository's applications are put together, who is allowed to call whom, and what happens to a request from a user's click through to a database write and back. Complements [overview.md](overview.md) (what's implemented) with a concrete call map. Facts checked against code on 2026-07-21 (`apps/api/app/bootstrap/app_factory.py`, `apps/api/app/main.py`).

## 1. Application map

| Application | Role | Technology | Storage |
|---|---|---|---|
| `apps/api` | The only source of business logic and the only writer to PostgreSQL | Python 3.12, FastAPI, Pydantic v2, psycopg | PostgreSQL (source of truth), Redis (cache, optional) |
| `apps/web` | The user-facing interface | Next.js 15 (App Router), React 19, TypeScript, next-intl, TanStack Query v5 | none of its own — reads `apps/api` over REST |
| `apps/notifier` | Telegram delivery and inbound Telegram updates | Go, gRPC, a Kafka consumer | MongoDB (derived, rebuildable state) |
| `apps/worker` | Batch jobs outside the request path (currently: processing `translation_jobs`) | a Python CLI | none of its own — connects directly to the same PostgreSQL as `apps/api`, running the same business logic as `/admin/translation-jobs/process-batch` |
| `packages/ui` | The design system: primitives, tokens, Storybook | React, CSS tokens | — |
| `packages/contracts/generated` | Generated TypeScript API types | generated from `contracts/openapi.yaml` | — |

Only `apps/api` is allowed to write to PostgreSQL. `apps/notifier` never connects
to PostgreSQL at all — it is strictly downstream: it learns about domain events
only through Kafka, keeps its own read/derived view of state in MongoDB, and can
fully rebuild that view from the Kafka log if it's lost (invariant §2 in
[invariants.md](invariants.md)). `apps/worker` connects to the same PostgreSQL
as `apps/api`, but only runs already-existing service logic — it is not an
independent source of business rules, just a second caller of the same
`app/services/*` code, running outside an HTTP request.

## 2. The synchronous path: a browser request to a response

```
apps/web (Server/Client Component)
   │  fetch(`${NEXT_PUBLIC_API_BASE_URL}/api/v1/...`), cache: "no-store", AbortSignal.timeout
   ▼
apps/api/app/api/v1/<router>.py         thin: parse path/query/body, dependencies
   │                                     (CurrentUser, require_roles/require_capability,
   │                                     get_connection), call exactly one service function
   ▼
apps/api/app/services/<domain>*.py      all business logic; large domains become a
   │                                     package (services/<domain>/{helpers.py, ...},
   │                                     __init__.py re-exports the public surface)
   ▼
apps/api/app/repositories/<domain>.py   SQL only; nothing resembling a decision
   │                                     belongs here (enforced by the
   │                                     "repository is SQL-only" test)
   ▼
PostgreSQL (psycopg, ConnectionPool)
```

The response travels back through the same layers. An error at any level becomes
the single envelope `api_error(status, code, message, details=None)`
(`apps/api/app/core/errors.py`, assembled into JSON in
`app_factory.error_response`) → `{"error": {"code", "message", "details"}}` — the
frontend parses exactly this shape (`apps/web/src/shared/api/http.ts`), never the
message text.

### Middleware (in the order they're attached, outermost first)

1. `request_id_middleware` — generates/forwards `X-Request-ID`, binds it to the
   logging context; survives even an early 403/429 from an inner middleware.
2. `metrics_middleware` — counts requests, latency, exports them via `/metrics`.
3. Rate limiting — a tighter limit on sensitive paths (`/api/v1/auth/login`,
   `/api/v1/auth/register`) than the general one.
4. CSRF double-submit — required for `POST/PUT/PATCH/DELETE` when the request
   carries a session cookie (not an `Authorization` header) and the path isn't on
   the exempt list (`/auth/login`, `/auth/register`).
5. `CORSMiddleware` — origins from `settings.cors_origins`, methods
   `GET/POST/PUT/PATCH/DELETE`.
6. Security headers — CSP, `Permissions-Policy`, and others, attached to every
   response.

## 3. The asynchronous path: a domain event to Telegram

```
apps/api/app/services/*.py
   │  a business transition (e.g.: a post is published, a reminder comes due)
   ▼
INSERT INTO domain_events (event_type, event_key, payload, notifiable)
   │  event_key guarantees idempotency; notifiable=FALSE for seed/historical
   │  events — no notification storm when data is bulk-loaded
   ▼
scripts/outbox_relay.py               a separate process/job, NOT part of the
   │  request: a short claim transaction → publish to Kafka outside any
   │  transaction → a short result-commit transaction (see invariants.md §2,
   │  items 9-10) — a Kafka outage never holds a long-lived DB transaction open
   ▼
Kafka (Redpanda)
   ▼
apps/notifier/internal/notifier/handler.go
   │  the consumer reads the event, resolves the channel (today: Telegram),
   │  formats the message IN THE RECIPIENT'S OWN LOCALE (internal/locale,
   │  from the Telegram update's language_code, captured on every user
   │  interaction with the bot)
   ▼
apps/notifier/internal/telegram/client.go → the Telegram Bot API (fake|real per TELEGRAM_MODE)
   │
   ▼ (on failure)
DLQ (internal/dlq) — the consumer never crashes, the event is never lost silently
```

The same pattern applies to `apps/web` ↔ `apps/notifier` for linking a Telegram
account: web calls `apps/api`, and `apps/api` calls the notifier over gRPC
(`apps/notifier/internal/grpcserver`) to verify/link — this is the only
synchronous path between the web backend and the Go service; everything else
flows one-way through Kafka.

## 4. Layer rules inside `apps/api`

| Layer | May import | Must not |
|---|---|---|
| `api/v1/*` (routers) | `services/*`, `schemas/*`, `core/*` | `repositories/*` directly, psycopg/SQL |
| `services/*` | `repositories/*`, other `services/*` through their public `__init__.py`, `core/*` | another domain's internal (`_private`) names, the HTTP layer |
| `repositories/*` | psycopg, `core/database` | `services/*` (never the other way — a repository knows nothing about business rules) |
| `schemas/*` | Pydantic, each other | `services/*`, `repositories/*` (schemas are pure data contracts) |
| `core/*` | third-party libraries | `api/v1/*`, `services/*`, `repositories/*` (core is the lowest layer; nothing above it is depended back on) |

Inside `services/`, once a domain grows into a package (threshold: ~800 lines,
house style in `.ai/project/12-domain-rules.md`), cross-cutting private helpers
live in a single `helpers.py` and are called via qualified module access
(`helpers.thing(...)`), never `from .helpers import thing` — otherwise
`monkeypatch.setattr` in tests silently stops intercepting the call. Platform
domains with an explicitly protected boundary (example — author metrics,
`services/author_metrics/`) are never imported by the platform's decision/CII
code at all: overlay endpoints read author data separately rather than folding
it into the core calculation — that's an invariant (invariants.md, item 3), not
just a convention.

## 5. `apps/web`: frontend layers

```
apps/web/src/
  app/[locale]/**        Next.js App Router: pages, layout, server components
  features/               complete user-facing flows (a form, a stateful block)
  entities/                domain entities: api.ts (TanStack Query hooks + query
                           keys), types come from packages/contracts/generated
  shared/                  reusable code with no domain meaning: api/http.ts
                           (the fetch wrapper, unified error parsing,
                           mutationErrorMessage), lib/ — UI primitives come from
                           packages/ui, never duplicated here
  i18n/                    next-intl config, routing (localePrefix: "always")
  messages/{en,ru,es}.json interface localization (not the backend's content data)
```

Every page on the public surface lives under `app/[locale]/...` — a locale
segment in the URL is mandatory (`localePrefix: "always"`, decision D-8).
`/internal/**` (the admin console) is the exception: its own
`NextIntlClientProvider` pinned to `locale="ru"`, outside the three-language
migration (decision D-12, see
[../decisions/open-questions.md](../decisions/open-questions.md)).

Every fetch to `apps/api` goes through `shared/api/http.ts`: a single timeout
point (`AbortSignal.timeout`), a single parser for
`{error:{code,message,details}}`, a single `mutationErrorMessage()` helper for
mutation error text. A raw `fetch()` to `/api/v1/...` from inside a component is
a boundary violation — a component should go through `entities/*/api.ts`.

## 6. `apps/notifier`: Go service layers

```
internal/
  kafka/          the domain-event consumer
  notifier/        orchestration: resolves the channel, the recipient's locale,
                   sends, handles failure
  channels/        the delivery-channel abstraction (today: one channel, Telegram)
  telegram/         the Bot API client, message formatting (client.go), the bot handler
  telegram/bot/     inbound Telegram update handling (messages.go — a string
                   catalog ×3 languages)
  locale/           a BCP-47 language_code → en|ru|es resolver (default ru)
  mongo/            derived state: the delivery log, TelegramIdentity (including Locale)
  dlq/              undelivered events — never lost silently
  grpc/, grpcserver/ the subscriptions server: Telegram↔web linking, called from apps/api
  subscriptions/    a service layer over mongo for linking/locale
  health/, metrics/, config/, events/   infrastructure packages
```

The dependency direction is strictly one way:
`kafka``notifier``channels``telegram`. `telegram/bot` (inbound updates from a
user) is the only place that writes `Locale` to Mongo; `notifier` (outbound
domain-event notifications) only reads that locale when formatting a message for
a given recipient. No `internal/*` package opens a PostgreSQL connection — if
the Go service ever needs data from PostgreSQL, that's a signal the missing
information belongs in the event payload or in a gRPC response from `apps/api`,
not behind direct access to someone else's database.

## 7. `apps/worker`: batch jobs outside the request path

A thin Python CLI (`apps/worker/country_decision_atlas_worker/main.py`) that
runs already-existing service logic in batches outside an HTTP request — today
the only command, `translation-jobs`, calls the same function as
`POST /admin/translation-jobs/process-batch`. It is not an independent source of
business rules: if a job needs new logic, that logic is added to
`apps/api/app/services/*` and reused, not duplicated inside the worker. Not yet
registered in `dev_tools_scripts_runner.py` and not mentioned in CI — run
manually (see [overview.md](overview.md) §4).

## 8. The contract between backend and frontend

```
apps/api/app/schemas/*.py (Pydantic v2)
        │  FastAPI auto-generates the OpenAPI schema from these
        ▼
contracts/openapi.yaml               source of truth, committed to git
        │  pnpm contracts:generate
        ▼
packages/contracts/generated/types.ts  generated TS types — NEVER hand-edited
        │  imported by
        ▼
apps/web/src/entities/*/api.ts        TanStack Query hooks, typed with the
                                        generated types
```

Any change to a request/response shape must go through this entire path in one
commit: edit `schemas/*.py` → `pnpm contracts:generate` → commit the updated
`types.ts` → update `apps/web` consumers. Hand-editing
`contracts/openapi.yaml` or `types.ts` outside this flow is forbidden — the
schema and the generated output would drift silently, with no compiler to catch
it.

## 9. Boundaries that must never be crossed

- `apps/notifier` never connects to PostgreSQL; `apps/api` never imports Go code
  (the only interaction is Kafka and gRPC).
- `apps/web` never reads the database directly — only through `/api/v1/*`.
- Inside `apps/api/app/services/`, domains with an explicit boundary (author
  metrics, country contribution) are never mixed into platform-level
  calculations (CII, the decision engine, drift, trust) — only a read-only
  overlay through dedicated endpoints.
- No layer reads `os.environ` directly inside business logic — configuration
  flows through `app/core/config.py::get_settings()`, the single source of
  truth for settings.
- The full list of immutable architectural decisions lives in
  [invariants.md](invariants.md).
