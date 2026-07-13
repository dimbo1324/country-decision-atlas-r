"use client";

import { useEffect, useState } from "react";
import { cn } from "../lib/cn";
import { useReducedMotion } from "../hooks/useReducedMotion";
import type { CriteriaWeight } from "./types";

interface CriteriaWeightBarsProps {
  criteria: CriteriaWeight[];
  active: boolean;
}

/** Horizontal contribution bars for a decision score's breakdown: each
 * criterion's signed contribution grows from a shared zero baseline —
 * positive to the right (sage, unless the caller sets its own accent),
 * negative to the left (terra) — so bonuses and penalties read at a glance
 * without a legend. */
export function CriteriaWeightBars({
  criteria,
  active,
}: CriteriaWeightBarsProps) {
  const reducedMotion = useReducedMotion();
  const [entered, setEntered] = useState(false);
  const maxAbs =
    Math.max(1, ...criteria.map((item) => Math.abs(item.contribution))) || 1;

  useEffect(() => {
    if (!active) return;
    if (reducedMotion) {
      setEntered(true);
      return;
    }
    const raf = requestAnimationFrame(() => setEntered(true));
    return () => cancelAnimationFrame(raf);
  }, [active, reducedMotion]);

  return (
    <ul className="flex flex-col gap-3">
      {criteria.map((item) => {
        const isPositive = item.contribution >= 0;
        const magnitude = entered
          ? (Math.abs(item.contribution) / maxAbs) * 50
          : 0;
        const accentClass = item.accent
          ? undefined
          : isPositive
            ? "bg-sage"
            : "bg-terra";
        return (
          <li
            key={item.label}
            className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4"
          >
            <div className="relative h-2">
              <div className="bg-c4 absolute inset-y-0 left-1/2 w-px" />
              <div
                className={cn(
                  "absolute inset-y-0 transition-[width] duration-[900ms]",
                  accentClass,
                )}
                style={{
                  left: isPositive ? "50%" : `${50 - magnitude}%`,
                  width: `${magnitude}%`,
                  background: item.accent
                    ? `var(--color-${item.accent})`
                    : undefined,
                  transitionTimingFunction: "var(--ease-arrive)",
                }}
              />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-c2 text-[9px] tracking-[0.12em] whitespace-nowrap uppercase">
                {item.label}
              </span>
              <span
                className={cn(
                  "font-display text-sm font-bold",
                  isPositive ? "text-sage3" : "text-terra3",
                )}
              >
                {isPositive ? "+" : ""}
                {item.contribution}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
