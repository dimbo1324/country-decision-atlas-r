# Чек-лист задачи: аудит-эпизоды AE-1/AE-2/AE-3 (проверка) + стабилизация quality gate

Ветка: `fix/quality-gate-stabilization-v1` (от актуального `main`).

Задача 1: проверить, что аудит-эпизоды AE-1 (`fix/db-index-safety-v1`),
AE-2 (`fix/rate-limiting-v1` → `fix/login-rate-limiting-v1`) и AE-3
(`fix/session-security-v1`) из `docs/_arch_/09_План_устранения_аудита.md`
выполнены; при необходимости — доделать. AE-3 (усиленная сессионная
безопасность — ротация токена, видимость устройств, step-up reauth) не
упрощать, оставить как есть.

Задача 2: исправить все ошибки из последнего прогона
`python dev_tools_scripts_runner.py` (полный quality gate), чтобы прогон
был полностью зелёным. Работать в одной ветке, в конце — push на
удалённый `main`.

## 1. Проверка аудит-эпизодов 1–3

```text
[+] Прочитан docs/_arch_/09_План_устранения_аудита.md целиком
[+] git log подтверждает: коммиты AE-1 (d496f04), AE-2 (48a9950), AE-3
    (c8d7256), AE-4 (b7c356a) уже на main — отдельных веток
    fix/db-index-safety-v1 / fix/login-rate-limiting-v1 /
    fix/session-security-v1 не существует (смерджены и удалены)
[+] AE-1 подтверждён по коду: 0 вхождений `::text = %s` в
    apps/api/app/repositories/, тест-инвариант
    tests/test_repository_index_safety_invariant.py существует
[+] AE-2 подтверждён по коду: apps/api/app/services/rate_limiter.py
    существует, auth_login_max_failed_attempts в config.py,
    trusted_proxy_ips настроен и используется
[+] AE-3 подтверждён по коду: httponly=True на cookie сессии,
    httponly=False на CSRF-cookie (double-submit), require_step_up_
    reauthentication + current_password в /auth/sessions/revoke-all,
    ротация токена (auth_session_rotation_interval_minutes,
    previous_token_hash) — усиленная защита НЕ трогалась, оставлена как
    есть по прямому указанию владельца
[+] AE-3 подтверждён живым прогоном: все 5 сценариев
    web-mvp-session-security.spec.ts зелёные (httpOnly-cookie невидима
    для JS, CSRF-cookie видима, сессия переживает reload, revoke-all
    требует пароль, запрос без CSRF-заголовка получает 403)
[+] Найден и исправлен дрейф документации: план устранения аудита
    утверждал «не смерджена, ждёт explicit push/merge» для AE-1 и AE-2,
    хотя оба коммита уже на main — статусы обновлены на «реализовано и
    смерджено в main» с указанием хешей коммитов (AE-1/AE-2/AE-3/AE-4
    для единообразия), карта зависимостей в §1 тоже обновлена
[+] Вывод: все три запрошенных эпизода полностью выполнены, доделывать
    нечего — только устранён дрейф документации
```

## 2. Диагностика провалов quality gate

```text
[+] pnpm quality (prettier format:check) — падал на
    RadarChart.tsx/SparklineChart.tsx; на момент старта этой задачи
    владелец уже закоммитил форматирование сам (коммит ec12cc1) — на
    момент проверки уже зелёный, действий не потребовалось
[+] pnpm web:mvp:check (Playwright E2E) — 14 провалов, все с одинаковым
    паттерном: `strict mode violation: locator resolved to 2 elements`
    (дублирующийся h1/testid на страницах countries, routes, what-changed)
[+] Найдена первопричина: тот же баг, что был закрыт в Episode 14
    (см. память episode-gotchas-backend-tooling) — клиентский setState в
    AuthProvider на mount дублирует SSR-контент на force-dynamic
    страницах. Эпизод AE-3 переписал AuthProvider.tsx под httpOnly-cookie
    сессию и потерял оригинальный фикс (синхронная проверка localStorage
    перед эффектом), потому что localStorage больше не источник истины
```

## 3. Исправление

```text
[+] apps/web/src/shared/auth/session.ts: добавлена экспортируемая
    hasSessionCookie() — синхронная проверка наличия cda_csrf cookie
    (единственный клиентски видимый сигнал о сессии при httpOnly-архитектуре,
    занимает место прежней синхронной проверки localStorage-токена)
[+] apps/web/src/shared/auth/AuthProvider.tsx: isLoading инициализируется
    из hasSessionCookie() вместо всегда true; mount-эффект возвращается
    без единого setState, если cookie нет — анонимные посетители (основной
    случай во всех упавших тестах) больше не вызывают setState после
    монтирования вообще, что и было условием фикса в Episode 14
[+] pnpm --filter web typecheck / lint — чисто
[+] Playwright: 3 ранее упавших spec-файла (analytical-pages, routes,
    what-changed) — все 48 тестов зелёные
[+] Playwright: полный прогон — все 283 теста зелёные, включая
    session-security (AE-3) — регрессий нет
```

## 4. Финальная проверка

```text
[+] python dev_tools_scripts_runner.py --profile full — полностью зелёный:
    OK: 78, WARN: 1 (безобидное предупреждение о закешированной
    .tmp/full-check директории, не блокирует), FAIL: 0, SKIP: 1 (protoc,
    как и раньше — коммиченные .pb.go используются как есть)
[+] git status чист, изменены только 3 намеренных файла
[+] task-checklist.md обновлён (этот файл)
```

## 5. Публикация

```text
[+] Один коммит на всю работу (проверка аудит-эпизодов — без изменений
    кода — плюс фикс дублирования DOM и обновление статусов плана —
    логически одна задача «привести quality gate и план аудита в
    соответствие с реальностью»)
[+] git merge --ff-only в main, push origin main
```
