# Чек-лист задачи: AE-3 «Сессии и XSS-периметр» — вариант Б + усиленная защита

Цель: закрыть Аудит-эпизод 3 (`docs/_arch_/09_План_устранения_аудита.md`,
находки P0-2, P2-5) вариантом Б (httpOnly-cookie сессии + CSRF +
CSP/HSTS/Permissions-Policy), и дополнительно реализовать три меры
усиленной защиты, согласованные с владельцем сверх базового плана эпизода:

1. Короткоживущие ротируемые токены сессии (вместо статичного 7-дневного
   токена).
2. Видимость сессий/устройств + уведомление о входе с нового устройства.
3. Step-up повторная аутентификация для чувствительного действия
   (массовый отзыв сессий).

Ветка: `fix/session-security-v1` (совпадает с именем из плана эпизода).

## Подготовка

- [+] Прочитан весь раздел «Аудит-эпизод 3» плана устранения аудита.
- [+] Изучены текущие файлы: `services/auth.py`, `repositories/auth.py`,
      `core/auth.py`, `api/v1/auth.py`, `schemas/auth.py`,
      `bootstrap/app_factory.py`, `main.py`, `core/config.py`,
      миграция `044_auth_rbac.sql`.
- [+] Изучены фронтенд-файлы: `session.ts`, `AuthProvider.tsx`, `http.ts`,
      `auth.ts`/`data-quality.ts`/`migrationBoard.ts`/`watchlists.ts`
      (использование `authHeaders`), `AccountView.tsx`, `next.config.mjs`.
- [+] Подтверждено: `GET/DELETE /auth/sessions` и `POST
      /auth/sessions/revoke-all` уже существуют; `user_agent_hash`/
      `ip_hash` в схеме есть, но никогда не заполняются роутером — фиксируем
      это в этом же эпизоде, а не откладываем.
- [+] Подтверждено: `APP_ENV=local` по умолчанию в docker-compose и
      Playwright — `Secure`-флаг cookie должен быть условным
      (`app_env == "production"`), иначе локальная разработка и E2E
      сломаются на чистом http.

## Реализация — backend

- [+] Миграция `052_session_security_hardening.sql`: новые колонки
      `auth_sessions` (`previous_token_hash`, `previous_token_expires_at`,
      `rotated_at`, `device_label`, `ip_display`, `device_fingerprint_hash`),
      индекс на `previous_token_hash`; новая таблица
      `user_security_notifications` (уведомления о входе с нового
      устройства, с `acknowledged_at`); расширение
      `audit_events_action_check` значением `new_device_login`.
- [+] `core/config.py`: новые настройки — имена cookie сессии/CSRF,
      интервал/грация ротации токена, флаг HSTS (по умолчанию выключен —
      «за флагом» согласно плану эпизода).
- [+] `core/request_context.py` (новый): единая точка извлечения client IP
      с учётом доверенных прокси (вынесено из `main.py`, переиспользуется
      в auth-роутере) + вывод короткой читаемой метки устройства из
      User-Agent + маскирование IP для отображения.
- [+] `services/auth.py`: генерация CSRF-токена при логине; заполнение
      `device_label`/`ip_display`/`device_fingerprint_hash` при создании
      сессии; определение «нового устройства»; ротация токена сессии по
      истечении интервала (с grace-периодом на предыдущий токен);
      `require_step_up_reauthentication()` — повторная проверка пароля.
- [+] `repositories/auth.py`: обновлены `SESSION_FIELDS`,
      `create_auth_session`, `get_session_with_user_by_token_hash` (лукап
      с учётом grace-периода предыдущего токена), новая `rotate_session_token`,
      `has_prior_session_with_fingerprint`.
- [+] `repositories/security_notifications.py` (новый): создание/список/
      подтверждение уведомлений о новом устройстве.
- [+] `core/auth.py`: чтение токена сессии из cookie, если нет
      `Authorization`; проброс ротированного токена в `Response`
      (cookie + заголовок для API-клиентов).
- [+] `api/v1/auth.py`: `login`/`register` выставляют httpOnly cookie сессии
      и не-httpOnly cookie CSRF (двухканальный переходный период — тело
      ответа тоже содержит токен); `logout` очищает обе cookie;
      `GET /auth/sessions` отдаёт `device_label`/`ip_display`/`is_current`;
      `POST /auth/sessions/revoke-all` требует `current_password` (step-up);
      новые `GET /auth/security-notifications`,
      `POST /auth/security-notifications/{id}/ack`.
- [+] `schemas/auth.py`: расширены `AuthSession`, новые
      `RevokeAllSessionsRequest`, `SecurityNotification*`.
- [+] `bootstrap/app_factory.py`: `CORSMiddleware.allow_credentials=True`;
      security-headers — CSP, Permissions-Policy, HSTS (за флагом), убран
      устаревший `X-XSS-Protection`; новый `csrf_protection_middleware`
      (double-submit, исключения для `/auth/login`/`/auth/register` и
      запросов с `Authorization`).
- [+] `main.py`: `_rate_limit_client` переведён на общий
      `core/request_context.py`.
- [+] `contracts/openapi.yaml` + `pnpm contracts:generate`.

## Реализация — frontend

- [+] `shared/auth/session.ts`: убраны localStorage-хелперы токена; новый
      `csrfHeaders()` читает CSRF-cookie.
- [+] `shared/auth/AuthProvider.tsx`: не хранит токен в localStorage,
      полагается на httpOnly cookie; `refresh()` больше не блокируется
      отсутствием токена в localStorage.
- [+] `shared/api/http.ts`: `credentials: "include"` на все четыре метода.
- [+] `shared/api/auth.ts`, `data-quality.ts`, `migrationBoard.ts`,
      `watchlists.ts`: `authHeaders` → `csrfHeaders` (механическое
      переименование под новую семантику).
- [+] `next.config.mjs`: заголовки CSP/Permissions-Policy/X-Frame-Options/
      X-Content-Type-Options/Referrer-Policy.
- [+] `AccountView.tsx`: показ устройства/IP по сессии, отметка текущей
      сессии, баннер «вход с нового устройства» с подтверждением,
      запрос пароля перед «Отозвать все сессии».

## Тесты

- [+] Unit: ротация токена (актуальный + grace-период предыдущего),
      определение нового устройства, step-up отклоняет неверный пароль,
      CSRF-мидлварь пропускает/блокирует по матрице случаев.
- [+] Миграционный тест на новые колонки/таблицу/constraint.
- [+] Обновлены существующие `test_auth_sessions.py`/`test_auth_api.py`
      под новые поля без потери покрытия старого поведения.
- [+] Playwright: логин выставляет httpOnly cookie сессии (JS не может её
      прочитать), сессия переживает reload без localStorage, мутирующий
      запрос без CSRF-заголовка получает 403 (там, где это проверяемо на
      уровне E2E), существующие auth/RBAC сценарии не регрессируют.

## Проверка

- [ ] `py -3.12 -m pytest tests/ -q` зелёный.
- [ ] `py -3.12 -m mypy apps scripts tests` чистый.
- [ ] `py -3.12 -m ruff check` / `ruff format --check` чистые.
- [ ] `pnpm --filter web typecheck` / `lint` чистые.
- [ ] Полный quality gate (`python dev_tools_scripts_runner.py full-check`)
      зелёный, включая Playwright E2E.

## Завершение

- [ ] Чек-лист заполнен `+`/`-`.
- [ ] `docs/_arch_/09_План_устранения_аудита.md`: статус AE-3 обновлён.
- [ ] Финальный отчёт написан (включая явно обозначенные компромиссы:
      `script-src 'unsafe-inline'` в CSP как принятый временный шаг вместо
      nonce-based CSP; уведомление о новом устройстве — только через
      собственный in-app баннер, без внешней интеграции, по правилу
      автономной разработки).
- [ ] Коммит, merge в `main` (ff-only), push на `origin/main` — по прямому
      запросу владельца (уже дан).
