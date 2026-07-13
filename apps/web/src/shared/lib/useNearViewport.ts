"use client";

import { useEffect, useState, type RefObject } from "react";

/** Gates a heavy section's query behind proximity to the viewport, so the
 * dossier's first paint stays light and full data loads in as the reader
 * scrolls (plan §Этап 6, "паттерн ленивой загрузки секций"). Once true,
 * stays true — sections don't unmount their data when scrolled past. */
export function useNearViewport(ref: RefObject<Element | null>): boolean {
  const [isNear, setIsNear] = useState(false);

  useEffect(() => {
    if (isNear) return;
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setIsNear(true);
        }
      },
      { rootMargin: "200px 0px" },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, [ref, isNear]);

  return isNear;
}
