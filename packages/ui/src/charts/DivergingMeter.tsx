"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { readCssVar } from "../lib/color";
import type { Accent } from "../lib/accents";
import { accentCssVar, type ChartMode } from "./types";

interface DivergingMeterProps {
  categories: string[];
  leftLabel: string;
  rightLabel: string;
  leftValues: number[];
  rightValues: number[];
  leftAccent: Accent;
  rightAccent: Accent;
  active: boolean;
  maxValue?: number;
  /** @default "live" */
  mode?: ChartMode;
  /** This package has no i18n context of its own (Storybook renders it
   * with none at all) — callers with a real locale pass the translated
   * string; untranslated callers keep the original Russian default. */
  scaleLabel?: string;
}

// Deliberately plain HTML/CSS instead of canvas: three rounds of bugs in the
// old canvas-drawn diverging bar chart (rows clipping, resize desync, hover
// geometry drifting off-canvas) all traced back to hand-rolled pixel math.
// CSS width percentages can't desync from their container — there's no
// backing-store/CSS-box pair to keep in sync, no manual row-height math, and
// browser layout does the resize handling for free.
export function DivergingMeter({
  categories,
  leftLabel,
  rightLabel,
  leftValues,
  rightValues,
  leftAccent,
  rightAccent,
  active,
  maxValue = 100,
  mode = "live",
  scaleLabel = "Балл · шкала 0–100",
}: DivergingMeterProps) {
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const [left, setLeft] = useState(leftValues);
  const [right, setRight] = useState(rightValues);
  const baseLeft = useRef(leftValues);
  const baseRight = useRef(rightValues);

  useEffect(() => {
    baseLeft.current = leftValues;
    baseRight.current = rightValues;
    setLeft(leftValues);
    setRight(rightValues);
  }, [leftValues, rightValues]);

  useEffect(() => {
    if (!active || effectiveMode !== "live") return;
    const id = window.setInterval(() => {
      setLeft(
        baseLeft.current.map((value) =>
          Math.min(maxValue, Math.max(0, value + (Math.random() - 0.5) * 6)),
        ),
      );
      setRight(
        baseRight.current.map((value) =>
          Math.min(maxValue, Math.max(0, value + (Math.random() - 0.5) * 6)),
        ),
      );
    }, 2200);
    return () => window.clearInterval(id);
  }, [active, effectiveMode, maxValue]);

  const leftColor = readCssVar(accentCssVar(leftAccent)) || "#d8aa4e";
  const rightColor = readCssVar(accentCssVar(rightAccent)) || "#5f93bd";

  return (
    <div className="flex h-full flex-col gap-5">
      <div className="font-mono text-c4 flex items-center justify-between text-[9px] tracking-[0.2em] uppercase">
        <span style={{ color: leftColor }}>{leftLabel}</span>
        <span>{scaleLabel}</span>
        <span style={{ color: rightColor }}>{rightLabel}</span>
      </div>
      <div className="flex flex-1 flex-col justify-center gap-5">
        {categories.map((category, i) => (
          <div
            key={category}
            className="grid grid-cols-[1fr_auto_1fr] items-center gap-3"
          >
            <div className="flex items-center justify-end gap-2">
              <span
                className="font-display w-7 shrink-0 text-right text-sm font-bold"
                style={{ color: leftColor }}
              >
                {Math.round(left[i] ?? 0)}
              </span>
              <div className="border-warm relative h-2 w-full overflow-hidden rounded-full border">
                <div
                  className="absolute inset-y-0 right-0 rounded-full transition-[width] duration-[1400ms] ease-out"
                  style={{
                    width: `${((left[i] ?? 0) / maxValue) * 100}%`,
                    backgroundColor: leftColor,
                  }}
                />
              </div>
            </div>

            <span className="font-mono text-c2 px-1 text-center text-[10px] tracking-[0.1em] whitespace-nowrap uppercase">
              {category}
            </span>

            <div className="flex items-center gap-2">
              <div className="border-warm relative h-2 w-full overflow-hidden rounded-full border">
                <div
                  className="absolute inset-y-0 left-0 rounded-full transition-[width] duration-[1400ms] ease-out"
                  style={{
                    width: `${((right[i] ?? 0) / maxValue) * 100}%`,
                    backgroundColor: rightColor,
                  }}
                />
              </div>
              <span
                className="font-display w-7 shrink-0 text-left text-sm font-bold"
                style={{ color: rightColor }}
              >
                {Math.round(right[i] ?? 0)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
