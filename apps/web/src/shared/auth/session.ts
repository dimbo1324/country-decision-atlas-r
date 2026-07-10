const CSRF_COOKIE_NAME = "cda_csrf";

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

export function hasSessionCookie(): boolean {
  return readCookie(CSRF_COOKIE_NAME) !== null;
}
