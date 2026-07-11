import { useRef, useState } from "react";
import { cn } from "@/lib/cn";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";
import { Drawer } from "@/components/ui/Drawer";
import { SparklineChart } from "@/components/charts/SparklineChart";
import type { DriftBoardRow } from "@/data/generator";

const STATUS_STYLES: Record<
  DriftBoardRow["status"],
  { badge: string; colorVar: string }
> = {
  pos: { badge: "border-sage2 text-sage3", colorVar: "--color-sage3" },
  mild: { badge: "border-blue2 text-blue3", colorVar: "--color-blue3" },
  stable: { badge: "border-warm-hi text-c3", colorVar: "--color-c3" },
  neg: { badge: "border-terra2 text-terra3", colorVar: "--color-terra3" },
};

function RowSparkline({
  values,
  colorVar,
  active,
}: {
  values: number[];
  colorVar: string;
  active: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentRef = useRef<number[]>(values.map(() => 0));
  const targetRef = useRef<number[]>(values);
  const tickRef = useRef(0);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (tickRef.current % 170 === 0) {
        const spread =
          (Math.max(...values) - Math.min(...values)) * 0.08 || 0.6;
        targetRef.current = values.map(
          (value) => value + (Math.random() - 0.5) * spread,
        );
      }
      const min = Math.min(...values);
      const max = Math.max(...values);
      const range = max - min || 1;
      const color = readCssVar(colorVar) || "#827a6a";
      ctx.clearRect(0, 0, width, height);
      ctx.beginPath();
      currentRef.current.forEach((value, i) => {
        const next = lerp(value, targetRef.current[i], 0.06);
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
    active,
  );

  return (
    <canvas
      ref={canvasRef}
      className="h-6 w-full"
    />
  );
}

interface DriftBoardProps {
  rows: DriftBoardRow[];
  active: boolean;
}

/** The mockup's drift board: one row per jurisdiction with a live inline
 * sparkline and a direction badge. Clicking a row opens its dossier. */
export function DriftBoard({ rows, active }: DriftBoardProps) {
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
                  colorVar={style.colorVar}
                  active={active}
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
        eyebrow={selected ? `Дрейф · REF CA-2026-${selected.flag}` : ""}
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
                  Чистый дрейф · 16 нед.
                </div>
              </div>
              <div>
                <div className="font-display text-c1 text-3xl font-bold">
                  {selected.statusLabel}
                </div>
                <div className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
                  Направление
                </div>
              </div>
            </div>
            <div className="h-44">
              <SparklineChart
                values={selected.timeline}
                active={selected !== null}
                colorVar={STATUS_STYLES[selected.status].colorVar}
                zeroLine
                yAxisLabel="Индекс дрейфа"
                xAxisLabel="16 недель"
              />
            </div>
            <p className="text-c3 text-sm leading-relaxed">
              Дрейф взвешивается по уровню воздействия каждого правового
              сигнала. При выборке менее трёх событий за окно платформа честно
              помечает результат как «недостаточно данных» и не показывает
              ложный тренд.
            </p>
            <p className="font-quote text-c4 text-xs italic">
              Это не юридическая консультация — данные носят справочный
              характер.
            </p>
          </div>
        )}
      </Drawer>
    </>
  );
}
