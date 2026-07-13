"use client";

import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "../hooks/useReducedMotion";
import type { Accent } from "../lib/accents";
import { accentCssVar, type ChartMode } from "./types";

interface ProgressRingProps {
  /** 0..100 */
  value: number;
  label: string;
  size?: number;
  accent?: Accent;
  active: boolean;
  suffix?: string;
  /** @default "live" */
  mode?: ChartMode;
}

export function ProgressRing({
  value,
  label,
  size = 168,
  accent = "gold",
  active,
  suffix = "",
  mode = "live",
}: ProgressRingProps) {
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const [armed, setArmed] = useState(false);
  const [display, setDisplay] = useState(0);
  const [ringValue, setRingValue] = useState(0);
  const startedRef = useRef(false);

  const stroke = 3;
  const radius = size / 2 - stroke * 2;
  const circumference = 2 * Math.PI * radius;
  const shownRing = armed ? ringValue : 0;

  // Entrance: arm the dashoffset transition one frame after activation so the
  // ring visibly fills from zero (CSS transitions need a rendered "from"
  // state), and run the counter with the same ease-out cubic as every number
  // here. The *text* number always settles at the exact value — only the
  // ring's fill (ringValue) keeps moving afterwards, and only in live mode.
  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (reducedMotion) {
      setArmed(true);
      setDisplay(value);
      setRingValue(value);
      return;
    }
    const raf = requestAnimationFrame(() => setArmed(true));
    const start = performance.now();
    const durationMs = 1400;
    const step = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - (1 - progress) ** 3;
      setDisplay(Math.round(value * eased));
      setRingValue(value * eased);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [active, reducedMotion, value]);

  // Live mode: once armed, the ring's fill breathes gently around the real
  // value forever — the text number above never moves, only this decorative
  // stroke-dashoffset does (design-system rule: breathing never contradicts
  // the labeled figure).
  useEffect(() => {
    if (!active || !armed || effectiveMode !== "live") return;
    const id = window.setInterval(() => {
      const wobble = (Math.random() - 0.5) * 3;
      setRingValue(Math.min(100, Math.max(0, value + wobble)));
    }, 1800);
    return () => window.clearInterval(id);
  }, [active, armed, effectiveMode, value]);

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="absolute inset-0"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-c5)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`var(${accentCssVar(accent)})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - shownRing / 100)}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{
            transition: reducedMotion
              ? "none"
              : effectiveMode === "live"
                ? "stroke-dashoffset 1.6s ease-in-out"
                : "stroke-dashoffset 1.4s var(--ease-arrive)",
          }}
        />
      </svg>
      <div className="flex flex-col items-center gap-1">
        <span
          className="font-display text-4xl leading-none font-bold"
          style={{ color: `var(${accentCssVar(accent)})` }}
        >
          {display}
          {suffix}
        </span>
        <span className="font-mono text-c3 max-w-[80%] text-center text-[9px] tracking-[0.2em] uppercase">
          {label}
        </span>
      </div>
    </div>
  );
}
