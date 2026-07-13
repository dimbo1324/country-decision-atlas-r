"use client";

import { type RefObject, useEffect, useRef } from "react";

export function useCanvasLoop(
  ref: RefObject<HTMLCanvasElement | null>,
  draw: (ctx: CanvasRenderingContext2D, width: number, height: number) => void,
  active: boolean,
) {
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || !active) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Keep the canvas backing store in sync with its CSS box every frame,
    // measuring fresh (never caching) so any layout shift — width OR height —
    // is picked up on the next frame instead of drawing past a stale buffer.
    const syncSize = (cssWidth: number, cssHeight: number) => {
      const ratio = window.devicePixelRatio || 1;
      const nextWidth = Math.max(1, Math.round(cssWidth * ratio));
      const nextHeight = Math.max(1, Math.round(cssHeight * ratio));
      if (canvas.width !== nextWidth || canvas.height !== nextHeight) {
        canvas.width = nextWidth;
        canvas.height = nextHeight;
      }
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    };

    const paint = () => {
      const rect = canvas.getBoundingClientRect();
      syncSize(rect.width, rect.height);
      draw(ctx, rect.width, rect.height);
    };

    const tick = () => {
      paint();
      frameRef.current = requestAnimationFrame(tick);
    };

    const stop = () => {
      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current);
        frameRef.current = null;
      }
    };

    // Paint synchronously instead of waiting for the first rAF tick: a fresh
    // mount (e.g. the fullscreen chart overlay, which remounts this
    // component into a portal) must show a correct frame immediately, not an
    // empty canvas for one frame while the first rAF callback is pending.
    const start = () => {
      if (frameRef.current !== null) return;
      paint();
      frameRef.current = requestAnimationFrame(tick);
    };

    // A hidden browser tab has no visible pixels to paint, so a *transition*
    // to hidden stops the loop instead of drawing into the void every frame —
    // resumes with a fresh paint on the transition back to visible. The
    // initial mount always starts regardless of the current
    // visibilityState: headless/automated browsers (Playwright, this
    // project's own Storybook preview under browser automation) commonly
    // report "hidden" for an unfocused-but-still-rendering tab, and gating
    // the first start on that would silently stop every canvas chart from
    // ever drawing under CI/E2E.
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        stop();
      } else {
        start();
      }
    };

    start();
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      stop();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, ref]);
}

export function lerp(current: number, target: number, factor = 0.055): number {
  return current + (target - current) * factor;
}
