"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "../lib/cn";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { accentCssVar, type ChartMode, type DonutSegment } from "./types";

interface DonutChartProps {
  segments: DonutSegment[];
  centerValue: string;
  centerLabel: string;
  active: boolean;
  size?: number;
  /** @default "live" */
  mode?: ChartMode;
}

export function DonutChart({
  segments,
  centerValue,
  centerLabel,
  active,
  size = 190,
  mode = "live",
}: DonutChartProps) {
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const [progress, setProgress] = useState(0);
  const [hovered, setHovered] = useState<number | null>(null);
  const [liveValues, setLiveValues] = useState(segments.map((s) => s.value));
  const baseValues = useRef(segments.map((s) => s.value));
  const startedRef = useRef(false);

  useEffect(() => {
    baseValues.current = segments.map((s) => s.value);
    setLiveValues(segments.map((s) => s.value));
  }, [segments]);

  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (reducedMotion) {
      setProgress(1);
      return;
    }
    const start = performance.now();
    const durationMs = 1300;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / durationMs);
      setProgress(1 - (1 - p) ** 3);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [active, reducedMotion]);

  // Live mode: each segment's *drawn* arc length breathes gently around its
  // real share — the center readout and legend percentages below always show
  // the exact base value, never the breathing one.
  useEffect(() => {
    if (!active || effectiveMode !== "live" || progress < 1) return;
    const id = window.setInterval(() => {
      setLiveValues(
        baseValues.current.map((value) =>
          Math.max(0, value + (Math.random() - 0.5) * (value * 0.08 || 1)),
        ),
      );
    }, 2000);
    return () => window.clearInterval(id);
  }, [active, effectiveMode, progress]);

  const stroke = 14;
  const radius = size / 2 - stroke;
  const circumference = 2 * Math.PI * radius;
  const drawnValues =
    effectiveMode === "live" ? liveValues : baseValues.current;
  const total = drawnValues.reduce((sum, value) => sum + value, 0) || 1;

  let offsetAccumulator = 0;

  return (
    <div className="flex items-center gap-7">
      <div
        className="relative shrink-0"
        style={{ width: size, height: size }}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          aria-hidden="true"
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-c5)"
            strokeWidth={1}
          />
          {segments.map((segment, index) => {
            const fraction = (drawnValues[index] / total) * progress;
            const dash = circumference * fraction;
            // 2px gap between segments so they read as separate inlays.
            const visibleDash = Math.max(0, dash - 2);
            const startOffset = offsetAccumulator;
            offsetAccumulator += dash;
            const isDimmed = hovered !== null && hovered !== index;
            return (
              <circle
                key={segment.label}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={`var(${accentCssVar(segment.accent)})`}
                strokeWidth={hovered === index ? stroke + 4 : stroke}
                strokeDasharray={`${visibleDash} ${circumference - visibleDash}`}
                strokeDashoffset={-startOffset}
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
                onMouseEnter={() => setHovered(index)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer transition-[stroke-width,opacity] duration-300"
                style={{ opacity: isDimmed ? 0.3 : 1 }}
              />
            );
          })}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-1">
          <span className="font-display text-c1 text-3xl leading-none font-bold">
            {hovered !== null ? `${segments[hovered].value}%` : centerValue}
          </span>
          <span className="font-mono text-c3 max-w-[70%] text-center text-[8px] tracking-[0.18em] uppercase">
            {hovered !== null ? segments[hovered].label : centerLabel}
          </span>
        </div>
      </div>

      <ul className="flex flex-col gap-2.5">
        {segments.map((segment, index) => (
          <li key={segment.label}>
            <button
              type="button"
              onMouseEnter={() => setHovered(index)}
              onMouseLeave={() => setHovered(null)}
              className={cn(
                "flex items-center gap-2.5 text-left transition-opacity duration-300",
                hovered !== null && hovered !== index && "opacity-40",
              )}
            >
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ background: `var(${accentCssVar(segment.accent)})` }}
              />
              <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
                {segment.label}
              </span>
              <span className="font-display text-c1 ml-1 text-xs font-bold">
                {segment.value}%
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
