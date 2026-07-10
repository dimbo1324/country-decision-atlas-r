const CSRF_COOKIE_NAME = "cda_csrf";
// First-party hint, set by this app on its own origin — deliberately NOT a
// read of cda_session/cda_csrf. Those are set by the API's Set-Cookie
// response and, whenever the API is deployed on a different host than the
// frontend (a separate API subdomain in prod; 127.0.0.1 vs localhost in
// CI), the browser stores them under the API's origin. document.cookie can
// never see a cookie belonging to a different origin, no matter what
// CORS/credentials settings say — that's a same-origin boundary, not a
// config knob. This hint cookie sidesteps the problem entirely by being
// written by the frontend itself right after a successful auth check.
const SESSION_HINT_COOKIE_NAME = "cda_session_hint";

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((entry) => entry.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.slice(name.length + 1)) : null;
}

export function csrfHeaders(): HeadersInit {
  const token = readCookie(CSRF_COOKIE_NAME);
  return token ? { "X-CSRF-Token": token } : {};
}

export function hasSessionHint(): boolean {
  return readCookie(SESSION_HINT_COOKIE_NAME) !== null;
}

export function setSessionHint(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${SESSION_HINT_COOKIE_NAME}=1; path=/; SameSite=Lax`;
}

export function clearSessionHint(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${SESSION_HINT_COOKIE_NAME}=; path=/; max-age=0`;
}
