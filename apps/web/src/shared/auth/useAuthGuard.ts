"use client";

import { useAuth } from "./AuthProvider";
import { hasRole } from "./roles";

export type AuthGuardStatus =
  | "loading"
  | "unauthenticated"
  | "forbidden"
  | "ok";

/** Centralizes the loading/unauthenticated/forbidden/ok decision that used
 * to be re-derived ad hoc in every gated view. Callers keep their own
 * messaging and data-testids per status — this hook only owns the branch
 * itself, not the rendered notice. */
export function useAuthGuard(roles?: Set<string>): {
  status: AuthGuardStatus;
  user: ReturnType<typeof useAuth>["user"];
} {
  const { user, isLoading } = useAuth();

  if (isLoading) return { status: "loading", user };
  if (!user) return { status: "unauthenticated", user };
  if (roles && !hasRole(user, roles)) return { status: "forbidden", user };
  return { status: "ok", user };
}
