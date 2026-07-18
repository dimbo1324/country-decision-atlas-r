import "@testing-library/jest-dom/vitest";
import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

// Without `test.globals: true` in vitest.config.ts, Testing Library's
// automatic per-test cleanup (which detects a *global* afterEach) never
// registers, so unmounted components pile up in the DOM across tests in
// the same file. Wiring it explicitly here avoids turning on `globals`
// project-wide just for this.
afterEach(() => {
  cleanup();
});

// jsdom has no IntersectionObserver; DossierRail (packages/ui) and other
// scrollspy-style components construct one unconditionally on mount.
class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | Document | null = null;
  readonly rootMargin: string = "";
  readonly thresholds: ReadonlyArray<number> = [];
  disconnect(): void {}
  observe(): void {}
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
  unobserve(): void {}
}
vi.stubGlobal("IntersectionObserver", MockIntersectionObserver);

// jsdom has no ResizeObserver either; HorizontalPager (packages/ui) reads
// its container's width this way to drive the pixel-based slide transform.
class MockResizeObserver implements ResizeObserver {
  disconnect(): void {}
  observe(): void {}
  unobserve(): void {}
}
vi.stubGlobal("ResizeObserver", MockResizeObserver);
