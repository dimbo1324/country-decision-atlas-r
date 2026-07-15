"use client";

import { useRef } from "react";
import { useCanvasLoop, lerp } from "../hooks/useCanvasLoop";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { readCssVar, withAlpha } from "../lib/color";
import type { Accent } from "../lib/accents";
import { accentCssVar, type ChartMode, type HeatmapData } from "./types";
import { useChartVisible } from "./useChartVisibility";

interface HeatmapProps {
  data: HeatmapData;
  active: boolean;
  accent?: Accent;
  /** @default "live" */
  mode?: ChartMode;
}

const LABEL_GUTTER_LEFT = 96;
const LABEL_GUTTER_BOTTOM = 24;
const CELL_GAP = 3;

export function Heatmap({
  data,
  active,
  accent = "terra",
  mode = "live",
}: HeatmapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isVisible = useChartVisible(canvasRef);
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const stateRef = useRef({
    current: data.values.map((row) => row.map(() => 0)),
    target: data.values.map((row) => [...row]),
  });
  const tickRef = useRef(0);
  // Mouse position lives in a ref so hover never restarts the draw loop —
  // the loop reads the latest cell under the cursor on every frame.
  const mouseRef = useRef<{ x: number; y: number } | null>(null);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (effectiveMode === "live" && tickRef.current % 160 === 0) {
        stateRef.current.target = data.values.map((row) =>
          row.map((value) =>
            Math.min(100, Math.max(0, value + (Math.random() - 0.5) * 7)),
          ),
        );
      }

      const rows = data.rows.length;
      const cols = data.columns.length;
      const plotW = width - LABEL_GUTTER_LEFT;
      const plotH = height - LABEL_GUTTER_BOTTOM;
      const cellW = (plotW - CELL_GAP * (cols - 1)) / cols;
      const cellH = (plotH - CELL_GAP * (rows - 1)) / rows;
      const color = readCssVar(accentCssVar(accent)) || "#c47553";
      const textColor = readCssVar("--color-c3") || "#827a6a";
      const brightText = readCssVar("--color-c1") || "#efe6d4";

      ctx.clearRect(0, 0, width, height);

      let hoveredCell: { row: number; col: number; value: number } | null =
        null;

      for (let row = 0; row < rows; row += 1) {
        for (let col = 0; col < cols; col += 1) {
          const next = reducedMotion
            ? stateRef.current.target[row][col]
            : lerp(
                stateRef.current.current[row][col],
                stateRef.current.target[row][col],
                0.05,
              );
          stateRef.current.current[row][col] = next;

          const x = LABEL_GUTTER_LEFT + col * (cellW + CELL_GAP);
          const y = row * (cellH + CELL_GAP);
          const mouse = mouseRef.current;
          const isHovered =
            mouse !== null &&
            mouse.x >= x &&
            mouse.x <= x + cellW &&
            mouse.y >= y &&
            mouse.y <= y + cellH;
          if (isHovered) {
            hoveredCell = { row, col, value: Math.round(next) };
          }

          // Intensity maps to alpha over the block accent — reads as ink
          // saturation on paper rather than a rainbow scale.
          const intensity = 0.06 + (next / 100) * 0.72;
          ctx.fillStyle = withAlpha(color, intensity);
          ctx.fillRect(x, y, cellW, cellH);
          if (isHovered) {
            ctx.strokeStyle = withAlpha(brightText, 0.7);
            ctx.lineWidth = 1;
            ctx.strokeRect(x + 0.5, y + 0.5, cellW - 1, cellH - 1);
          }
        }
      }

      ctx.font = "9px 'Courier New', monospace";
      ctx.textAlign = "right";
      ctx.textBaseline = "middle";
      data.rows.forEach((rowLabel, row) => {
        const y = row * (cellH + CELL_GAP) + cellH / 2;
        const isRowHovered = hoveredCell !== null && hoveredCell.row === row;
        ctx.fillStyle = isRowHovered ? withAlpha(brightText, 0.95) : textColor;
        ctx.fillText(
          rowLabel.toUpperCase(),
          LABEL_GUTTER_LEFT - 10,
          y,
          LABEL_GUTTER_LEFT - 14,
        );
      });

      ctx.textAlign = "center";
      ctx.textBaseline = "alphabetic";
      data.columns.forEach((columnLabel, col) => {
        const x = LABEL_GUTTER_LEFT + col * (cellW + CELL_GAP) + cellW / 2;
        const isColHovered = hoveredCell !== null && hoveredCell.col === col;
        ctx.fillStyle = isColHovered ? withAlpha(brightText, 0.95) : textColor;
        ctx.fillText(columnLabel.toUpperCase(), x, height - 8);
      });

      // Hover readout: value pinned to the top-right corner of the plot, in
      // the reserved gutter space, never following the cursor around.
      if (hoveredCell) {
        ctx.textAlign = "right";
        ctx.fillStyle = withAlpha(brightText, 0.9);
        ctx.font = "bold 12px 'Playfair Display', Georgia, serif";
        ctx.fillText(String(hoveredCell.value), width - 4, 12);
        ctx.fillStyle = textColor;
        ctx.font = "8px 'Courier New', monospace";
        ctx.fillText(
          `${data.rows[hoveredCell.row]} · ${data.columns[hoveredCell.col]}`.toUpperCase(),
          width - 4,
          24,
        );
      }
    },
    active && isVisible,
  );

  // Canvas has no accessible content of its own; a full per-cell readout
  // would be too long for a screen reader to be useful, so this gives the
  // grid shape plus the extremes -- enough to know what the chart shows.
  const flatValues = data.values.flat();
  const max = flatValues.length ? Math.max(...flatValues) : 0;
  const min = flatValues.length ? Math.min(...flatValues) : 0;
  const summary = `Тепловая карта: ${data.rows.length} строк (${data.rows.join(", ")}), ${data.columns.length} столбцов (${data.columns.join(", ")}). Значения от ${min} до ${max}.`;

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
      role="img"
      aria-label={summary}
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        mouseRef.current = {
          x: event.clientX - rect.left,
          y: event.clientY - rect.top,
        };
      }}
      onMouseLeave={() => {
        mouseRef.current = null;
      }}
    />
  );
}
