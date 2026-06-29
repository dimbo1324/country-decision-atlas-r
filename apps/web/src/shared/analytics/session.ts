const STORAGE_KEY = "cda_anonymous_session_id";

function createAnonymousSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;
}

export function getOrCreateAnonymousSessionId(): string {
  const nextId = createAnonymousSessionId();
  if (typeof window === "undefined") {
    return nextId;
  }
  try {
    const existing = window.localStorage.getItem(STORAGE_KEY);
    if (existing) {
      return existing;
    }
    window.localStorage.setItem(STORAGE_KEY, nextId);
    return nextId;
  } catch {
    return nextId;
  }
}
