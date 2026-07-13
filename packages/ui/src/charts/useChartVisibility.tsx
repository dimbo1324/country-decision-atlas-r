"use client";

import {
  createContext,
  type ReactNode,
  type RefObject,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

interface VisibilityRegistry {
  observe(element: Element, onChange: (visible: boolean) => void): () => void;
}

// No provider present (a standalone Storybook story, a chart dropped in
// without a surrounding page) means "always visible" — the exact behavior
// every chart already had before this registry existed, so nothing breaks
// for a call site that hasn't opted in.
const noopRegistry: VisibilityRegistry = {
  observe(_element, onChange) {
    onChange(true);
    return () => {};
  },
};

const ChartVisibilityContext = createContext<VisibilityRegistry>(noopRegistry);

interface ChartVisibilityProviderProps {
  children: ReactNode;
  /** Pre-activate charts slightly before they enter the viewport so the
   * first visible frame isn't a cold start. */
  rootMargin?: string;
}

/** One shared `IntersectionObserver` for every canvas chart under it, so a
 * page with many charts (a scrollable dossier, a promo deck) only keeps the
 * RAF loop running for the chart(s) actually on screen. */
export function ChartVisibilityProvider({
  children,
  rootMargin = "200px",
}: ChartVisibilityProviderProps) {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const callbacksRef = useRef(new Map<Element, (visible: boolean) => void>());
  const registryRef = useRef<VisibilityRegistry>({
    observe(element, onChange) {
      if (!observerRef.current) {
        observerRef.current = new IntersectionObserver(
          (entries) => {
            for (const entry of entries) {
              callbacksRef.current.get(entry.target)?.(entry.isIntersecting);
            }
          },
          { rootMargin },
        );
      }
      callbacksRef.current.set(element, onChange);
      observerRef.current.observe(element);
      return () => {
        callbacksRef.current.delete(element);
        observerRef.current?.unobserve(element);
      };
    },
  });

  useEffect(() => {
    const observer = observerRef.current;
    return () => observer?.disconnect();
  }, []);

  return (
    <ChartVisibilityContext.Provider value={registryRef.current}>
      {children}
    </ChartVisibilityContext.Provider>
  );
}

/** Registers `ref`'s current element with the nearest visibility registry and
 * returns whether it's currently in view (or always `true` outside a
 * provider). Combine with a chart's own `active` prop:
 * `useCanvasLoop(ref, draw, active && isVisible)`. */
export function useChartVisible(ref: RefObject<Element | null>): boolean {
  const registry = useContext(ChartVisibilityContext);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    return registry.observe(element, setVisible);
  }, [ref, registry]);

  return visible;
}
