"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { readCssVar } from "../lib/color";
import type { Accent } from "../lib/accents";
import { accentCssVar, type ChartMode } from "./types";

interface BarColumnsProps {
  items: { label: string; value: number }[];
  active: boolean;
  accent?: Accent;
  maxValue?: number;
  /** @default "live" */
  mode?: ChartMode;
}

// Plain HTML/CSS like DivergingMeter: percentage heights can't desync from
// their container, and browser layout does all resize handling for free.
export function BarColumns({
  items,
  active,
  accent = "blue",
  maxValue = 100,
  mode = "live",
}: BarColumnsProps) {
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const [values, setValues] = useState(items.map(() => 0));
  const [hovered, setHovered] = useState<number | null>(null);
  const baseRef = useRef(items.map((item) => item.value));

  useEffect(() => {
    baseRef.current = items.map((item) => item.value);
    if (reducedMotion) {
      setValues(items.map((item) => item.value));
      return;
    }
    // Grow from zero on (re)mount, then breathe around the base.
    const raf = requestAnimationFrame(() =>
      setValues(items.map((item) => item.value)),
    );
    return () => cancelAnimationFrame(raf);
  }, [items, reducedMotion]);

  useEffect(() => {
    if (!active || effectiveMode !== "live") return;
    const id = window.setInterval(() => {
      setValues(
        baseRef.current.map((value) =>
          Math.min(maxValue, Math.max(2, value + (Math.random() - 0.5) * 8)),
        ),
      );
    }, 2400);
    return () => window.clearInterval(id);
  }, [active, effectiveMode, maxValue]);

  const color = readCssVar(accentCssVar(accent)) || "#92bce0";

  return (
    <div className="flex h-full flex-col gap-3">
      <div className="flex flex-1 items-end justify-between gap-3">
        {items.map((item, index) => (
          <div
            key={item.label}
            className="group flex h-full flex-1 flex-col items-center justify-end gap-2"
            onMouseEnter={() => setHovered(index)}
            onMouseLeave={() => setHovered(null)}
          >
            <span
              className="font-display text-sm font-bold transition-opacity duration-300"
              style={{
                color,
                opacity: hovered === index ? 1 : 0,
              }}
            >
              {Math.round(values[index] ?? 0)}
            </span>
            <div className="border-warm relative w-full flex-1 overflow-hidden border">
              <div
                className="absolute inset-x-0 bottom-0 transition-[height] duration-[1400ms]"
                style={{
                  height: `${((values[index] ?? 0) / maxValue) * 100}%`,
                  background: color,
                  opacity: hovered === null || hovered === index ? 0.85 : 0.3,
                  transitionTimingFunction: "var(--ease-arrive)",
                }}
              />
            </div>
            <span className="font-mono text-c3 text-[8px] tracking-[0.12em] uppercase">
              {item.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
