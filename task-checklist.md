# Чек-лист задачи: GitHub Actions «Playwright E2E» падал после предыдущего пуша

Ветка: `fix/ci-cross-origin-cookie-visibility-v1` (от `main`).

Владелец сообщил, что GitHub Actions ругается на предыдущий коммит
(`21ae6e0`): job «Playwright E2E» упал с 9 провалами, все — вокруг
логина/сессии/CSRF (session-security, watchlist, migration-board create,
auth-rbac). Локальный `dev_tools_scripts_runner.py` был зелёным перед тем
коммитом — расхождение означает разницу в окружении CI vs локально.

## 1. Диагностика

```text
[+] Прочитан лог провала из GitHub Actions — все 9 провалов завязаны на
    залогиненное состояние (session-security 4/5 тестов, watchlist 3/3,
    migration-board create, auth-rbac "regular user" проверка)
[+] Найдено расхождение в .github/workflows/quality.yml (job e2e): фронтенд
    поднимается на WEB_BASE_URL по умолчанию (http://localhost:3000), а
    API — на NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 (шаг «Run
    frontend regression gate»). localhost и 127.0.0.1 — РАЗНЫЕ origin'ы
    для скоупинга cookie в браузере, даже если оба резолвятся на loopback
[+] Подтверждено: document.cookie на странице localhost:3000 в принципе не
    может увидеть cookie, установленную ответом с 127.0.0.1:8000, — это
    жёсткая граница same-origin в браузере, её нельзя обойти никакими
    CORS/credentials-настройками
[+] Из этого следует два независимых сломанных механизма:
    1. AuthProvider.tsx (мой предыдущий коммит 21ae6e0): hasSessionCookie()
       читал document.cookie на cda_csrf — в CI всегда возвращал false,
       блокируя refresh() навсегда, даже для реально залогиненных
       пользователей после reload/навигации
    2. csrfHeaders() в session.ts (существовал ДО моего коммита,
       независимо): тоже читает document.cookie на cda_csrf для
       прикрепления X-CSRF-Token к мутирующим запросам — в CI всегда
       возвращал {}, все POST/PATCH/DELETE получали 403 от CSRF-мидлвари
[+] Локально воспроизведено: собрал фронтенд с
    NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 (эмулируя точный CI-
    конфиг) — получил ТЕ ЖЕ 9 провалов, что и в GitHub Actions
```

## 2. Исправление

```text
[+] .github/workflows/quality.yml: NEXT_PUBLIC_API_BASE_URL/API_BASE_URL в
    шаге «Run frontend regression gate» изменены с http://127.0.0.1:8000
    на http://localhost:8000 — совпадает с WEB_BASE_URL по умолчанию;
    сам uvicorn остаётся на --host 127.0.0.1 (не менялось, localhost:8000
    резолвится туда же на раннере)
[+] apps/web/src/shared/auth/session.ts + AuthProvider.tsx: hasSessionCookie
    (чтение cda_csrf) заменён на hasSessionHint/setSessionHint/
    clearSessionHint — cookie cda_session_hint, которую фронтенд
    устанавливает САМ на своём собственном origin сразу после успешного
    login/register/refresh (и чистит на logout/провале refresh). Это
    устойчиво к любому расхождению origin фронтенда и API (не только в
    этом CI-конфиге, но и в потенциальном будущем проде на отдельном
    поддомене API) — синхронный сигнал больше не зависит от того, видна
    ли cookie ДРУГОГО origin
[!] Важное ограничение зафиксировано явно: hint-cookie решает только
    геймтинг AuthProvider (избегать лишний setState/дублирование DOM для
    анонимных посетителей). Он НЕ и не может починить csrfHeaders() —
    видимость cda_csrf для JS фундаментально требует same-origin (или
    Domain=-расшаривания), обойти это на фронтенде невозможно в принципе.
    Поэтому выравнивание хостов в CI — обязательная часть фикса, не
    опциональная; сам по себе hint-cookie её не заменяет
```

## 3. Проверка

```text
[+] pnpm --filter web typecheck / lint — чисто
[+] Сборка с NEXT_PUBLIC_API_BASE_URL=127.0.0.1:8000 (искусственно
    воспроизводя старый сломанный конфиг) — подтверждено, что hint-cookie
    сам по себе НЕ чинит csrfHeaders()-зависимые тесты (CSRF-cookie
    readable, mutating-request-without-csrf, migration-board create) —
    это ожидаемо и задокументировано выше, не баг реализации
[+] Пересборка со значениями по умолчанию (оба localhost — то, что
    реально будет использовано в CI после фикса workflow) — полный
    прогон Playwright: 283/283 зелёных, включая все 9 ранее упавших
[+] python dev_tools_scripts_runner.py --profile full — полностью
    зелёный: OK 78, WARN 0, FAIL 0, SKIP 1 (protoc, как обычно)
[+] git status чист, изменены только 3 намеренных файла
```

## 4. Публикация

```text
[+] Один коммит (диагностика CI-расхождения + оба фикса — воркфлоу и
    hint-cookie — логически одна задача «почему CI ругался и как это
    исправлено»)
[+] git merge --ff-only в main, push origin main
```
