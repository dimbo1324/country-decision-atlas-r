"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "../hooks/useReducedMotion";

interface CounterProps {
  value: number;
  suffix?: string;
  active: boolean;
  durationMs?: number;
}

export function Counter({
  value,
  suffix = "",
  active,
  durationMs = 1400,
}: CounterProps) {
  const [display, setDisplay] = useState(0);
  const startedRef = useRef(false);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    // Matches every other animated primitive in the kit: skip the count-up
    // entirely and show the final value when reduced motion is requested.
    if (reducedMotion) {
      setDisplay(value);
      return;
    }
    const start = performance.now();

    let raf = 0;
    const step = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - (1 - progress) ** 3;
      setDisplay(Math.round(value * eased));
      if (progress < 1) raf = requestAnimationFrame(step);
    };
    raf = requestAnimationFrame(step);
    // Without this the recursive loop keeps running (and calling setState)
    // after unmount, and a deps change would start a second loop racing the
    // first one for the same state.
    return () => cancelAnimationFrame(raf);
  }, [active, durationMs, value, reducedMotion]);

  return (
    <span>
      {display}
      {suffix}
    </span>
  );
}
