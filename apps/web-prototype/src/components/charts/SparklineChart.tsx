import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

interface SparklineChartProps {
  values: number[];
  active: boolean;
  colorVar: string;
  zeroLine?: boolean;
}

export function SparklineChart({
  values,
  active,
  colorVar,
  zeroLine = false,
}: SparklineChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentRef = useRef<number[]>(values.map(() => 0));
  const targetRef = useRef<number[]>(values);
  const tickRef = useRef(0);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (tickRef.current % 130 === 0) {
        const spread = (Math.max(...values) - Math.min(...values)) * 0.06 || 1;
        targetRef.current = values.map(
          (value) => value + (Math.random() - 0.5) * spread,
        );
      }

      const min = Math.min(...values, 0);
      const max = Math.max(...values, 1);
      const range = max - min || 1;
      const padX = 6;
      const padY = 12;
      const plotW = width - padX * 2;
      const plotH = height - padY * 2;
      const color = readCssVar(colorVar) || "#d8aa4e";
      const border = readCssVar("--color-c5") || "#2a2832";

      ctx.clearRect(0, 0, width, height);

      if (zeroLine) {
        const zeroY = padY + plotH - ((0 - min) / range) * plotH;
        ctx.strokeStyle = withAlpha(border, 0.8);
        ctx.setLineDash([3, 4]);
        ctx.beginPath();
        ctx.moveTo(padX, zeroY);
        ctx.lineTo(width - padX, zeroY);
        ctx.stroke();
        ctx.setLineDash([]);
      }

      const points = currentRef.current.map((value, i) => {
        const next = lerp(value, targetRef.current[i], 0.06);
        currentRef.current[i] = next;
        const x = padX + (plotW * i) / (values.length - 1);
        const y = padY + plotH - ((next - min) / range) * plotH;
        return { x, y };
      });

      const gradient = ctx.createLinearGradient(0, padY, 0, padY + plotH);
      gradient.addColorStop(0, withAlpha(color, 0.28));
      gradient.addColorStop(1, withAlpha(color, 0));
      ctx.beginPath();
      ctx.moveTo(points[0].x, padY + plotH);
      points.forEach((point) => ctx.lineTo(point.x, point.y));
      ctx.lineTo(points[points.length - 1].x, padY + plotH);
      ctx.closePath();
      ctx.fillStyle = gradient;
      ctx.fill();

      ctx.beginPath();
      points.forEach((point, i) => {
        if (i === 0) ctx.moveTo(point.x, point.y);
        else ctx.lineTo(point.x, point.y);
      });
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.75;
      ctx.lineJoin = "round";
      ctx.stroke();

      const last = points[points.length - 1];
      ctx.beginPath();
      ctx.arc(last.x, last.y, 3, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
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
