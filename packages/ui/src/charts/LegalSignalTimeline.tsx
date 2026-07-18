"use client";

import { useEffect, useMemo, useState } from "react";
import { scaleTime } from "d3-scale";
import { cn } from "../lib/cn";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { accentCssVar } from "./types";
import type { Accent } from "../lib/accents";
import type { LegalSignalEvent } from "./types";

interface LegalSignalTimelineProps {
  events: LegalSignalEvent[];
  active: boolean;
  width?: number;
  height?: number;
  /** This package has no i18n context of its own (Storybook renders it
   * with none at all) — callers with a real locale build and pass the
   * translated, already-interpolated string; untranslated callers keep
   * the original Russian default. */
  ariaLabel?: string;
}

const IMPACT_ACCENT: Record<LegalSignalEvent["impact"], Accent> = {
  up: "sage",
  down: "terra",
  info: "blue",
};

const PAD_X = 48;
const AXIS_Y_RATIO = 0.42;

/** Horizontal timeline of legal-signal events. Built directly on `d3-scale`
 * (just the time axis) rather than a library timeline component — the
 * mockup's engraved-ledger aesthetic (alternating stagger, mono date labels,
 * impact-colored markers) doesn't map onto any off-the-shelf timeline's
 * styling surface. */
export function LegalSignalTimeline({
  events,
  active,
  width = 760,
  height = 180,
  ariaLabel,
}: LegalSignalTimelineProps) {
  const reducedMotion = useReducedMotion();
  const [entered, setEntered] = useState(false);

  const sorted = useMemo(
    () =>
      [...events].sort(
        (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime(),
      ),
    [events],
  );

  const scale = useMemo(() => {
    const dates = sorted.map((event) => new Date(event.date));
    const min = dates[0] ?? new Date();
    const max = dates[dates.length - 1] ?? min;
    return scaleTime()
      .domain(
        min.getTime() === max.getTime()
          ? [min, new Date(min.getTime() + 1)]
          : [min, max],
      )
      .range([PAD_X, width - PAD_X]);
  }, [sorted, width]);

  useEffect(() => {
    if (!active) return;
    if (reducedMotion) {
      setEntered(true);
      return;
    }
    const raf = requestAnimationFrame(() => setEntered(true));
    return () => cancelAnimationFrame(raf);
  }, [active, reducedMotion]);

  const axisY = height * AXIS_Y_RATIO;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="h-full w-full"
      role="img"
      aria-label={
        ariaLabel ?? `Таймлайн правовых сигналов, ${sorted.length} событий`
      }
    >
      <line
        x1={PAD_X}
        y1={axisY}
        x2={width - PAD_X}
        y2={axisY}
        stroke="var(--color-c4)"
        strokeWidth={1}
      />
      {sorted.map((event, index) => {
        const x = scale(new Date(event.date));
        const stagger = index % 2 === 0;
        const labelY = stagger ? axisY - 20 : axisY + 32;
        const tickY2 = stagger ? axisY - 10 : axisY + 10;
        const accent = IMPACT_ACCENT[event.impact];
        return (
          <g
            key={event.id}
            style={{
              opacity: entered ? 1 : 0,
              transition: reducedMotion
                ? "none"
                : `opacity 0.5s var(--ease-reveal) ${index * 40}ms`,
            }}
          >
            <title>{`${event.date} · ${event.country} · ${event.title} — ${event.impactLabel}`}</title>
            <line
              x1={x}
              y1={axisY}
              x2={x}
              y2={tickY2}
              stroke={`var(${accentCssVar(accent)})`}
              strokeWidth={1}
            />
            <circle
              cx={x}
              cy={axisY}
              r={4}
              fill={`var(${accentCssVar(accent)})`}
            />
            <text
              x={x}
              y={labelY}
              textAnchor="middle"
              className={cn("font-mono", "fill-c3")}
              style={{ fontSize: 8, letterSpacing: "0.08em" }}
            >
              {event.date}
            </text>
            <text
              x={x}
              y={labelY + (stagger ? -10 : 10)}
              textAnchor="middle"
              className="fill-c2"
              style={{ fontSize: 9, fontFamily: "var(--font-body)" }}
            >
              {event.country}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
