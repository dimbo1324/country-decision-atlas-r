import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

export interface RadarSeries {
  label: string;
  values: number[];
  colorVar: string;
}

interface RadarChartProps {
  axes: string[];
  series: RadarSeries[];
  active: boolean;
  maxValue?: number;
}

export function RadarChart({
  axes,
  series,
  active,
  maxValue = 100,
}: RadarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stateRef = useRef<{ current: number[][]; target: number[][] }>({
    current: series.map((serie) => serie.values.map(() => 0)),
    target: series.map((serie) => serie.values),
  });
  const tickRef = useRef(0);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (tickRef.current % 150 === 0) {
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

      ctx.clearRect(0, 0, width, height);

      ctx.strokeStyle = withAlpha(border, 0.5);
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
        const color = readCssVar(serie.colorVar) || "#d8aa4e";
        const currentValues = stateRef.current.current[seriesIndex];
        const targetValues = stateRef.current.target[seriesIndex];

        ctx.beginPath();
        currentValues.forEach((value, i) => {
          const next = lerp(value, targetValues[i], 0.05);
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
    active,
  );

  return (
    <canvas
      ref={canvasRef}
      className="h-full w-full"
    />
  );
}
