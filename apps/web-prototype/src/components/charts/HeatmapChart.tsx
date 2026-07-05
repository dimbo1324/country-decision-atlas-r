import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

interface HeatmapChartProps {
  rows: string[];
  columns: string[];
  values: number[][];
  active: boolean;
}

export function HeatmapChart({
  rows,
  columns,
  values,
  active,
}: HeatmapChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentRef = useRef<number[][]>(values.map((row) => row.map(() => 0)));

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      const labelW = 84;
      const labelH = 22;
      const gap = 4;
      const cellW = (width - labelW) / columns.length;
      const cellH = (height - labelH) / rows.length;
      const gold = readCssVar("--color-gold") || "#d8aa4e";
      const bg5 = readCssVar("--color-c5") || "#2a2832";
      const textColor = readCssVar("--color-c2") || "#c0b6a0";

      ctx.clearRect(0, 0, width, height);
      ctx.font = "9px 'Courier New', monospace";
      ctx.textBaseline = "middle";

      columns.forEach((column, colIndex) => {
        const x = labelW + cellW * colIndex + cellW / 2;
        ctx.fillStyle = textColor;
        ctx.textAlign = "center";
        ctx.fillText(column.toUpperCase(), x, labelH / 2);
      });

      rows.forEach((row, rowIndex) => {
        const y = labelH + cellH * rowIndex + cellH / 2;
        ctx.fillStyle = textColor;
        ctx.textAlign = "left";
        ctx.fillText(row, 4, y);

        columns.forEach((_column, colIndex) => {
          const target = values[rowIndex][colIndex];
          const current = lerp(
            currentRef.current[rowIndex][colIndex],
            target,
            0.08,
          );
          currentRef.current[rowIndex][colIndex] = current;

          const x = labelW + cellW * colIndex;
          const intensity = Math.max(0.06, current / 100);
          ctx.fillStyle = withAlpha(bg5, 0.6);
          ctx.fillRect(
            x + gap / 2,
            y - cellH / 2 + gap / 2,
            cellW - gap,
            cellH - gap,
          );
          ctx.fillStyle = withAlpha(gold, intensity * 0.85);
          ctx.fillRect(
            x + gap / 2,
            y - cellH / 2 + gap / 2,
            cellW - gap,
            cellH - gap,
          );

          ctx.fillStyle = withAlpha(textColor, 0.9);
          ctx.textAlign = "center";
          ctx.fillText(String(Math.round(current)), x + cellW / 2, y);
        });
      });
    },
    active,
  );

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
    />
  );
}
