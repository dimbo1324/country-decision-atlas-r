"use client";

import { useRef } from "react";
import { useCanvasLoop, lerp } from "../hooks/useCanvasLoop";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { readCssVar, withAlpha } from "../lib/color";
import type { Accent } from "../lib/accents";
import { accentCssVar, type ChartMode } from "./types";
import { useChartVisible } from "./useChartVisibility";

export interface RadarSeries {
  label: string;
  values: number[];
  accent: Accent;
}

interface RadarChartProps {
  axes: string[];
  series: RadarSeries[];
  active: boolean;
  maxValue?: number;
  /** @default "live" */
  mode?: ChartMode;
}

export function RadarChart({
  axes,
  series,
  active,
  maxValue = 100,
  mode = "live",
}: RadarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isVisible = useChartVisible(canvasRef);
  const reducedMotion = useReducedMotion();
  // prefers-reduced-motion always wins over the caller's requested mode
  // (design-system §5: reduced motion degrades everything heavy to static).
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const stateRef = useRef<{ current: number[][]; target: number[][] }>({
    current: series.map((serie) => serie.values.map(() => 0)),
    target: series.map((serie) => serie.values),
  });
  const tickRef = useRef(0);
  // Hover is tracked in a ref (not state) so it never restarts useCanvasLoop's
  // effect — the running draw loop just reads the latest value each frame.
  const hoveredRef = useRef(false);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (effectiveMode === "live" && tickRef.current % 150 === 0) {
        stateRef.current.target = series.map((serie) =>
          serie.values.map((value) => {
            const wobble = (Math.random() - 0.5) * (maxValue * 0.03);
            return Math.min(maxValue, Math.max(0, value + wobble));
          }),
        );
      }

      const cx = width / 2;
      const cy = height / 2;
      const radius = Math.min(width, height) * 0.36;
      const step = (Math.PI * 2) / axes.length;
      const border = readCssVar("--color-c4") || "#494436";
      const textColor = readCssVar("--color-c3") || "#827a6a";
      const axisColor = readCssVar("--color-c2") || "#c0b6a0";
      const hovered = hoveredRef.current;

      ctx.clearRect(0, 0, width, height);

      ctx.strokeStyle = withAlpha(border, hovered ? 0.75 : 0.5);
      ctx.lineWidth = 1;
      for (let ring = 1; ring <= 4; ring += 1) {
        ctx.beginPath();
        for (let i = 0; i <= axes.length; i += 1) {
          const angle = -Math.PI / 2 + step * i;
          const r = (radius * ring) / 4;
          const x = cx + Math.cos(angle) * r;
          const y = cy + Math.sin(angle) * r;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        }
        ctx.stroke();
      }

      if (hovered) {
        ctx.save();
        // Spokes: one line per axis from center to the outer ring.
        ctx.strokeStyle = withAlpha(axisColor, 0.22);
        ctx.lineWidth = 1;
        axes.forEach((_axis, i) => {
          const angle = -Math.PI / 2 + step * i;
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(
            cx + Math.cos(angle) * radius,
            cy + Math.sin(angle) * radius,
          );
          ctx.stroke();
        });
        // Value scale along the top spoke (0/25/50/75/100). Same serif
        // display face as every other number in the app — mono is reserved
        // for uppercase text labels (the axis names below), never values.
        ctx.font = "bold 9px 'Playfair Display', Georgia, serif";
        ctx.fillStyle = withAlpha(axisColor, 0.8);
        ctx.textAlign = "left";
        for (let ring = 1; ring <= 4; ring += 1) {
          const r = (radius * ring) / 4;
          const value = Math.round((maxValue * ring) / 4);
          ctx.fillText(String(value), cx + 4, cy - r);
        }
        ctx.restore();
      }

      ctx.fillStyle = textColor;
      ctx.font = "9px 'Courier New', monospace";
      ctx.textAlign = "center";
      axes.forEach((axis, i) => {
        const angle = -Math.PI / 2 + step * i;
        const x = cx + Math.cos(angle) * (radius + 22);
        const y = cy + Math.sin(angle) * (radius + 22);
        ctx.fillText(axis.toUpperCase(), x, y);
      });

      series.forEach((serie, seriesIndex) => {
        const color = readCssVar(accentCssVar(serie.accent)) || "#d8aa4e";
        const currentValues = stateRef.current.current[seriesIndex];
        const targetValues = stateRef.current.target[seriesIndex];

        ctx.beginPath();
        currentValues.forEach((value, i) => {
          // Reduced motion: jump straight to the real value, no glide-in —
          // matching ProgressRing/GaugeArc/DonutChart's established
          // reduced-motion behavior (instant, not merely slower).
          const next = reducedMotion
            ? targetValues[i]
            : lerp(value, targetValues[i], 0.05);
          currentValues[i] = next;
          const angle = -Math.PI / 2 + step * i;
          const r = (radius * next) / maxValue;
          const x = cx + Math.cos(angle) * r;
          const y = cy + Math.sin(angle) * r;
          if (i === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.closePath();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.fillStyle = withAlpha(color, 0.12);
        ctx.fill();
        ctx.stroke();
      });
    },
    active && isVisible,
  );

  // Canvas has no accessible content of its own -- everything drawn on it
  // is invisible to screen readers unless summarized in an aria-label.
  const summary = series
    .map(
      (serie) =>
        `${serie.label}: ${axes.map((axis, i) => `${axis} ${Math.round(serie.values[i] ?? 0)}`).join(", ")}`,
    )
    .join("; ");

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
      role="img"
      aria-label={summary}
      onMouseEnter={() => {
        hoveredRef.current = true;
      }}
      onMouseLeave={() => {
        hoveredRef.current = false;
      }}
    />
  );
}
