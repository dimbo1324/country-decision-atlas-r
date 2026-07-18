"use client";

import { useRef, useState } from "react";
import { cn } from "../lib/cn";
import { useCanvasLoop, lerp } from "../hooks/useCanvasLoop";
import { useReducedMotion } from "../hooks/useReducedMotion";
import { readCssVar, withAlpha } from "../lib/color";
import { Drawer } from "../primitives/Drawer";
import { SparklineChart } from "./SparklineChart";
import { useChartVisible } from "./useChartVisibility";
import { accentCssVar, type ChartMode, type DriftBoardRow } from "./types";
import type { Accent } from "../lib/accents";

const STATUS_STYLES: Record<
  DriftBoardRow["status"],
  { badge: string; accent: Accent }
> = {
  pos: { badge: "border-sage2 text-sage3", accent: "sage" },
  mild: { badge: "border-blue2 text-blue3", accent: "blue" },
  stable: { badge: "border-warm-hi text-c3", accent: "gold" },
  neg: { badge: "border-terra2 text-terra3", accent: "terra" },
};

function RowSparkline({
  values,
  accent,
  active,
  mode,
}: {
  values: number[];
  accent: Accent;
  active: boolean;
  mode: ChartMode;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const isVisible = useChartVisible(canvasRef);
  const reducedMotion = useReducedMotion();
  const effectiveMode: ChartMode = reducedMotion ? "static" : mode;
  const currentRef = useRef<number[]>(values.map(() => 0));
  const targetRef = useRef<number[]>(values);
  const tickRef = useRef(0);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (effectiveMode === "live" && tickRef.current % 170 === 0) {
        const spread =
          (Math.max(...values) - Math.min(...values)) * 0.08 || 0.6;
        targetRef.current = values.map(
          (value) => value + (Math.random() - 0.5) * spread,
        );
      }
      const min = Math.min(...values);
      const max = Math.max(...values);
      const range = max - min || 1;
      const color = readCssVar(accentCssVar(accent)) || "#827a6a";
      ctx.clearRect(0, 0, width, height);
      ctx.beginPath();
      currentRef.current.forEach((value, i) => {
        const next = reducedMotion
          ? targetRef.current[i]
          : lerp(value, targetRef.current[i], 0.06);
        currentRef.current[i] = next;
        const x = (width * i) / (values.length - 1);
        const y = height - 3 - ((next - min) / range) * (height - 6);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = withAlpha(color, 0.85);
      ctx.lineWidth = 1.25;
      ctx.lineJoin = "round";
      ctx.stroke();
    },
    active && isVisible,
  );

  return (
    <canvas
      ref={canvasRef}
      className="h-6 w-full"
      aria-hidden="true"
    />
  );
}

export interface DriftBoardLabels {
  eyebrowPrefix: string;
  netDrift: string;
  direction: string;
  driftIndexAxis: string;
  weeksAxis: string;
  methodologyNote: string;
  legalDisclaimer: string;
}

const DEFAULT_LABELS: DriftBoardLabels = {
  eyebrowPrefix: "Дрейф · REF CA-2026-",
  netDrift: "Чистый дрейф · 16 нед.",
  direction: "Направление",
  driftIndexAxis: "Индекс дрейфа",
  weeksAxis: "16 недель",
  methodologyNote:
    "Дрейф взвешивается по уровню воздействия каждого правового сигнала. При выборке менее трёх событий за окно платформа честно помечает результат как «недостаточно данных» и не показывает ложный тренд.",
  legalDisclaimer:
    "Это не юридическая консультация — данные носят справочный характер.",
};

interface DriftBoardProps {
  rows: DriftBoardRow[];
  active: boolean;
  /** @default "live" */
  mode?: ChartMode;
  /** This package has no i18n context of its own (Storybook renders it
   * with none at all) — callers with a real locale pass translated
   * labels; untranslated callers keep the original Russian defaults. */
  labels?: Partial<DriftBoardLabels>;
}

/** The mockup's drift board: one row per jurisdiction with a live inline
 * sparkline and a direction badge. Clicking a row opens its dossier. */
export function DriftBoard({
  rows,
  active,
  mode = "live",
  labels,
}: DriftBoardProps) {
  const l = { ...DEFAULT_LABELS, ...labels };
  const [selected, setSelected] = useState<DriftBoardRow | null>(null);

  return (
    <>
      <ul className="flex flex-col">
        {rows.map((row) => {
          const style = STATUS_STYLES[row.status];
          return (
            <li key={row.slug}>
              <button
                type="button"
                onClick={() => setSelected(row)}
                className="group border-warm relative grid w-full grid-cols-[44px_1fr_minmax(70px,110px)_auto] items-center gap-4 border-b py-3 text-left"
              >
                <span className="font-mono text-c4 text-[9px] tracking-[0.2em]">
                  {row.flag}
                </span>
                <span className="font-body text-c2 group-hover:text-c1 truncate text-sm transition-colors duration-300">
                  {row.name}
                </span>
                <RowSparkline
                  values={row.timeline}
                  accent={style.accent}
                  active={active}
                  mode={mode}
                />
                <span
                  className={cn(
                    "font-mono shrink-0 border px-2 py-1 text-[8px] tracking-[0.15em] uppercase",
                    style.badge,
                  )}
                >
                  {row.statusLabel}
                </span>
                <span className="bg-gold2/70 absolute right-0 bottom-0 left-0 h-px origin-left scale-x-0 transition-transform duration-500 group-hover:scale-x-100" />
              </button>
            </li>
          );
        })}
      </ul>

      <Drawer
        open={selected !== null}
        onClose={() => setSelected(null)}
        accent="terra"
        eyebrow={selected ? `${l.eyebrowPrefix}${selected.flag}` : ""}
        title={selected?.name ?? ""}
      >
        {selected && (
          <div className="flex flex-col gap-6">
            <div className="flex gap-8">
              <div>
                <div className="font-display text-terra3 text-3xl font-bold">
                  {selected.driftValue > 0 ? "+" : ""}
                  {selected.driftValue}
                </div>
                <div className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
                  {l.netDrift}
                </div>
              </div>
              <div>
                <div className="font-display text-c1 text-3xl font-bold">
                  {selected.statusLabel}
                </div>
                <div className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
                  {l.direction}
                </div>
              </div>
            </div>
            <div className="h-44">
              <SparklineChart
                values={selected.timeline}
                active={selected !== null}
                accent={STATUS_STYLES[selected.status].accent}
                zeroLine
                yAxisLabel={l.driftIndexAxis}
                xAxisLabel={l.weeksAxis}
                mode={mode}
              />
            </div>
            <p className="text-c3 text-sm leading-relaxed">
              {l.methodologyNote}
            </p>
            <p className="font-quote text-c4 text-xs italic">
              {l.legalDisclaimer}
            </p>
          </div>
        )}
      </Drawer>
    </>
  );
}
