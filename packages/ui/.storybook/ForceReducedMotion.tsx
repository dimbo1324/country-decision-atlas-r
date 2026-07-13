import { type ReactNode, useEffect, useState } from "react";

/** Storybook-only helper: patches `matchMedia` so every `useReducedMotion()`
 * call inside `children` reads `prefers-reduced-motion: reduce` on its own
 * first mount. Children are withheld until the patch is active, so a chart's
 * `useState(() => matchMedia(...).matches)` initializer never races it.
 * Never imported by `src/index.ts` — story-only. */
export function ForceReducedMotion({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const original = window.matchMedia.bind(window);
    window.matchMedia = ((query: string) => {
      if (query.includes("prefers-reduced-motion")) {
        return {
          matches: true,
          media: query,
          onchange: null,
          addListener: () => {},
          removeListener: () => {},
          addEventListener: () => {},
          removeEventListener: () => {},
          dispatchEvent: () => false,
        } as MediaQueryList;
      }
      return original(query);
    }) as typeof window.matchMedia;
    setReady(true);
    return () => {
      window.matchMedia = original;
    };
  }, []);

  if (!ready) return null;
  return <>{children}</>;
}
