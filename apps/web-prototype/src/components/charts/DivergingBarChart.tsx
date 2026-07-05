import { useRef } from "react";
import { useCanvasLoop, lerp } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

interface DivergingBarChartProps {
  categories: string[];
  leftValues: number[];
  rightValues: number[];
  leftColorVar: string;
  rightColorVar: string;
  active: boolean;
  maxValue?: number;
}

export function DivergingBarChart({
  categories,
  leftValues,
  rightValues,
  leftColorVar,
  rightColorVar,
  active,
  maxValue = 100,
}: DivergingBarChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const currentLeftRef = useRef<number[]>(leftValues.map(() => 0));
  const currentRightRef = useRef<number[]>(rightValues.map(() => 0));
  const targetLeftRef = useRef<number[]>(leftValues);
  const targetRightRef = useRef<number[]>(rightValues);
  const tickRef = useRef(0);

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      tickRef.current += 1;
      if (tickRef.current % 140 === 0) {
        targetLeftRef.current = leftValues.map((value) =>
          Math.min(maxValue, Math.max(0, value + (Math.random() - 0.5) * 6)),
        );
        targetRightRef.current = rightValues.map((value) =>
          Math.min(maxValue, Math.max(0, value + (Math.random() - 0.5) * 6)),
        );
      }

      const labelZone = 116;
      const rowGap = 10;
      const rowHeight =
        (height - rowGap * (categories.length - 1)) / categories.length;
      const axisX = width / 2;
      const maxBarWidth = width / 2 - labelZone / 2 - 12;

      const leftColor = readCssVar(leftColorVar) || "#d8aa4e";
      const rightColor = readCssVar(rightColorVar) || "#5f93bd";
      const axisColor = readCssVar("--color-c4") || "#494436";
      const textColor = readCssVar("--color-c2") || "#c0b6a0";

      ctx.clearRect(0, 0, width, height);

      ctx.strokeStyle = withAlpha(axisColor, 0.7);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(axisX, 4);
      ctx.lineTo(axisX, height - 4);
      ctx.stroke();

      ctx.font = "11px 'Crimson Text', serif";
      ctx.textBaseline = "middle";

      categories.forEach((category, i) => {
        const rowY = i * (rowHeight + rowGap);
        const barCenterY = rowY + rowHeight / 2;

        const nextLeft = lerp(
          currentLeftRef.current[i],
          targetLeftRef.current[i],
          0.06,
        );
        currentLeftRef.current[i] = nextLeft;
        const nextRight = lerp(
          currentRightRef.current[i],
          targetRightRef.current[i],
          0.06,
        );
        currentRightRef.current[i] = nextRight;

        const leftWidth = (nextLeft / maxValue) * maxBarWidth;
        const rightWidth = (nextRight / maxValue) * maxBarWidth;
        const barThickness = Math.min(22, rowHeight * 0.6);

        ctx.fillStyle = withAlpha(leftColor, 0.75);
        ctx.strokeStyle = leftColor;
        ctx.lineWidth = 1.25;
        ctx.beginPath();
        ctx.rect(
          axisX - labelZone / 2 - leftWidth,
          barCenterY - barThickness / 2,
          leftWidth,
          barThickness,
        );
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = withAlpha(rightColor, 0.75);
        ctx.strokeStyle = rightColor;
        ctx.beginPath();
        ctx.rect(
          axisX + labelZone / 2,
          barCenterY - barThickness / 2,
          rightWidth,
          barThickness,
        );
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = withAlpha(leftColor, 0.95);
        ctx.textAlign = "right";
        ctx.font = "10px 'Courier New', monospace";
        ctx.fillText(
          String(Math.round(nextLeft)),
          axisX - labelZone / 2 - leftWidth - 6,
          barCenterY,
        );

        ctx.fillStyle = withAlpha(rightColor, 0.95);
        ctx.textAlign = "left";
        ctx.fillText(
          String(Math.round(nextRight)),
          axisX + labelZone / 2 + rightWidth + 6,
          barCenterY,
        );

        ctx.fillStyle = textColor;
        ctx.textAlign = "center";
        ctx.font = "11px 'Crimson Text', serif";
        ctx.fillText(category, axisX, barCenterY);
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
