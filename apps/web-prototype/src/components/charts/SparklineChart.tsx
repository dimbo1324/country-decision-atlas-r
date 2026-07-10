import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

interface SparklineChartProps {
  values: number[];
  active: boolean;
  colorVar: string;
  zeroLine?: boolean;
  /** Shown only on hover, positioned at the axis itself — not a floating
   * caption — so the chart stays legible on discovery, not by default. */
  yAxisLabel: string;
  xAxisLabel: string;
}

export function SparklineChart({
  values,
  active,
  colorVar,
  zeroLine = false,
  yAxisLabel,
  xAxisLabel,
}: SparklineChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentRef = useRef<number[]>(values.map(() => 0));
  const targetRef = useRef<number[]>(values);
  const tickRef = useRef(0);
  // Hover is tracked in a ref, not React state: the draw loop already reads
  // it fresh every frame, so toggling it never needs to restart useCanvasLoop's
  // effect (which would otherwise blank/re-init the chart on every hover).
  const hoveredRef = useRef(false);

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
      // Padding stays constant whether or not the axis labels are showing,
      // so hovering never shifts the plotted line/geometry. The left/bottom
      // margins are sized generously enough to fit a rotated axis title
      // plus the value-scale numbers without either ever colliding or
      // spilling past the canvas edge.
      const padX = 64;
      const padY = 32;
      const plotW = width - padX * 2;
      const plotH = height - padY * 2;
      const color = readCssVar(colorVar) || "#d8aa4e";
      const border = readCssVar("--color-c5") || "#2a2832";
      const axisColor = readCssVar("--color-c2") || "#c0b6a0";

      ctx.clearRect(0, 0, width, height);

      if (hoveredRef.current) {
        // Every hover element must stay within [padY, height - padY] /
        // [padX, width - padX] — that reserved margin is the only room
        // available without shifting the plotted line's geometry, and
        // anything drawn past it is silently clipped by the canvas edge.
        const xAxisY = padY + plotH;
        ctx.save();
        // Value numbers use the same serif display face as every other
        // number in the app (hero stats, metric cards) — mono stays
        // reserved for uppercase text labels, never for raw values, so
        // numbers read as one consistent family everywhere.
        ctx.font = "bold 10px 'Playfair Display', Georgia, serif";
        ctx.textBaseline = "middle";
        [max, (max + min) / 2, min].forEach((value) => {
          const y = padY + plotH - ((value - min) / range) * plotH;
          ctx.strokeStyle = withAlpha(axisColor, 0.18);
          ctx.setLineDash([2, 4]);
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(padX, y);
          ctx.lineTo(width - padX, y);
          ctx.stroke();
          ctx.setLineDash([]);
          ctx.fillStyle = withAlpha(axisColor, 0.75);
          ctx.textAlign = "right";
          ctx.fillText(value.toFixed(1), padX - 8, y);
        });
        ctx.strokeStyle = withAlpha(axisColor, 0.35);
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padX, padY);
        ctx.lineTo(padX, xAxisY);
        ctx.lineTo(width - padX, xAxisY);
        ctx.stroke();

        // Axis titles positioned at the axis itself, not a floating
        // caption: the Y title sits in the left margin, rotated so it
        // reads bottom-to-top alongside the vertical axis line; the X
        // title sits centered directly below the horizontal axis line,
        // reading left-to-right.
        ctx.fillStyle = withAlpha(axisColor, 0.7);
        ctx.font = "8px 'Courier New', monospace";

        ctx.save();
        ctx.translate(12, (padY + xAxisY) / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(yAxisLabel.toUpperCase(), 0, 0);
        ctx.restore();

        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillText(
          xAxisLabel.toUpperCase(),
          (padX + width - padX) / 2,
          xAxisY + 8,
        );
        ctx.restore();
      }

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
      onMouseEnter={() => {
        hoveredRef.current = true;
      }}
      onMouseLeave={() => {
        hoveredRef.current = false;
      }}
    />
  );
}
