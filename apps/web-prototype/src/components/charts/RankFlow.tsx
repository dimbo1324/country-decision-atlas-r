import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";
import type { RankFlowSeries } from "@/data/generator";

interface RankFlowProps {
  series: RankFlowSeries[];
  columns: string[];
  active: boolean;
}

const PAD_X = 90;
const PAD_TOP = 16;
const PAD_BOTTOM = 30;

/** Bump chart: rank positions (1 = top) flowing across quarters. */
export function RankFlow({ series, columns, active }: RankFlowProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  // Ranks are discrete; the drawn positions still lerp so a regenerated
  // dataset melts into its new ordering instead of snapping.
  const stateRef = useRef({
    current: series.map((serie) => serie.ranks.map(() => serie.ranks[0])),
    target: series.map((serie) => [...serie.ranks]),
  });
  const hoveredRef = useRef<number | null>(null);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      stateRef.current.target = series.map((serie) => [...serie.ranks]);

      const rowCount = series.length;
      const plotW = width - PAD_X * 2;
      const plotH = height - PAD_TOP - PAD_BOTTOM;
      const stepX = plotW / (columns.length - 1);
      const rowH = plotH / (rowCount - 1 || 1);
      const textColor = readCssVar("--color-c3") || "#827a6a";
      const brightText = readCssVar("--color-c1") || "#efe6d4";
      const gridColor = readCssVar("--color-c5") || "#2a2832";
      const hovered = hoveredRef.current;

      ctx.clearRect(0, 0, width, height);

      ctx.strokeStyle = withAlpha(gridColor, 0.7);
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 5]);
      columns.forEach((_, col) => {
        const x = PAD_X + col * stepX;
        ctx.beginPath();
        ctx.moveTo(x, PAD_TOP);
        ctx.lineTo(x, PAD_TOP + plotH);
        ctx.stroke();
      });
      ctx.setLineDash([]);

      ctx.font = "8px 'Courier New', monospace";
      ctx.fillStyle = textColor;
      ctx.textAlign = "center";
      columns.forEach((label, col) => {
        ctx.fillText(label.toUpperCase(), PAD_X + col * stepX, height - 10);
      });

      series.forEach((serie, seriesIndex) => {
        const color = readCssVar(serie.colorVar) || "#d8aa4e";
        const isDimmed = hovered !== null && hovered !== seriesIndex;
        const isHovered = hovered === seriesIndex;
        const points = serie.ranks.map((_, col) => {
          const next = lerp(
            stateRef.current.current[seriesIndex][col],
            stateRef.current.target[seriesIndex][col],
            0.07,
          );
          stateRef.current.current[seriesIndex][col] = next;
          return {
            x: PAD_X + col * stepX,
            y: PAD_TOP + (next - 1) * rowH,
          };
        });

        ctx.beginPath();
        points.forEach((point, col) => {
          if (col === 0) {
            ctx.moveTo(point.x, point.y);
            return;
          }
          // Soft S-curve between columns — flowing lanes, not a zigzag.
          const prev = points[col - 1];
          const midX = (prev.x + point.x) / 2;
          ctx.bezierCurveTo(midX, prev.y, midX, point.y, point.x, point.y);
        });
        ctx.strokeStyle = withAlpha(color, isDimmed ? 0.14 : 0.9);
        ctx.lineWidth = isHovered ? 2.5 : 1.5;
        ctx.stroke();

        points.forEach((point) => {
          ctx.beginPath();
          ctx.arc(point.x, point.y, isHovered ? 3.5 : 2.5, 0, Math.PI * 2);
          ctx.fillStyle = withAlpha(color, isDimmed ? 0.2 : 1);
          ctx.fill();
        });

        const last = points[points.length - 1];
        ctx.font = isHovered
          ? "bold 10px 'Courier New', monospace"
          : "9px 'Courier New', monospace";
        ctx.textAlign = "left";
        ctx.fillStyle = isDimmed
          ? withAlpha(textColor, 0.35)
          : isHovered
            ? brightText
            : withAlpha(color, 0.95);
        ctx.fillText(serie.name.toUpperCase(), last.x + 10, last.y + 3);

        const first = points[0];
        ctx.textAlign = "right";
        ctx.font = "bold 11px 'Playfair Display', Georgia, serif";
        ctx.fillStyle = isDimmed
          ? withAlpha(textColor, 0.3)
          : withAlpha(color, 0.9);
        ctx.fillText(`#${serie.ranks[0]}`, first.x - 10, first.y + 3);
      });
    },
    active,
  );

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
      onMouseMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        const y = event.clientY - rect.top;
        const plotH = rect.height - PAD_TOP - PAD_BOTTOM;
        const rowH = plotH / (series.length - 1 || 1);
        // Snap to the nearest lane by the series' *current drawn* rank at
        // the cursor's column, so hover follows the visible lines.
        const x = event.clientX - rect.left;
        const stepX = (rect.width - PAD_X * 2) / (columns.length - 1);
        const col = Math.min(
          columns.length - 1,
          Math.max(0, Math.round((x - PAD_X) / stepX)),
        );
        let best: number | null = null;
        let bestDistance = 18;
        stateRef.current.current.forEach((ranks, seriesIndex) => {
          const laneY = PAD_TOP + (ranks[col] - 1) * rowH;
          const distance = Math.abs(laneY - y);
          if (distance < bestDistance) {
            bestDistance = distance;
            best = seriesIndex;
          }
        });
        hoveredRef.current = best;
      }}
      onMouseLeave={() => {
        hoveredRef.current = null;
      }}
    />
  );
}
