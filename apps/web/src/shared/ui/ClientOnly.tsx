"use client";

import { useEffect, useState, type ReactNode } from "react";

/** Renders `fallback` on the server and on the very first client paint, then
 * swaps to `children` after mount.
 *
 * Used to wrap data views whose content is fetched entirely client-side
 * (TanStack Query with no SSR dehydration) and that read the URL via
 * `useSearchParams`/nuqs inside a `<Suspense>`. Such a boundary suspends
 * during SSR and emits a loading fallback, but the server-vs-client
 * reconciliation of that suspended boundary intermittently (dev) / reliably
 * (prod) diverges — React hydration error #418. Since the server can only
 * ever render the loading state for these views anyway, gating them behind a
 * mount flag makes SSR and the first client render emit the *same* fallback
 * markup (a plain div, not a suspended boundary), which hydrates cleanly; the
 * real content then mounts client-side. No SSR content is lost. */
export function ClientOnly({
  children,
  fallback,
}: {
  children: ReactNode;
  fallback: ReactNode;
}) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return <>{mounted ? children : fallback}</>;
}
