import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/cn";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import type { DonutSegment } from "@/data/generator";

interface DonutChartProps {
  segments: DonutSegment[];
  centerValue: string;
  centerLabel: string;
  active: boolean;
  size?: number;
}

export function DonutChart({
  segments,
  centerValue,
  centerLabel,
  active,
  size = 190,
}: DonutChartProps) {
  const reducedMotion = useReducedMotion();
  const [progress, setProgress] = useState(0);
  const [hovered, setHovered] = useState<number | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (reducedMotion) {
      setProgress(1);
      return;
    }
    const start = performance.now();
    const durationMs = 1300;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / durationMs);
      setProgress(1 - (1 - p) ** 3);
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [active, reducedMotion]);

  const stroke = 14;
  const radius = size / 2 - stroke;
  const circumference = 2 * Math.PI * radius;
  const total = segments.reduce((sum, segment) => sum + segment.value, 0) || 1;

  let offsetAccumulator = 0;

  return (
    <div className="flex items-center gap-7">
      <div
        className="relative shrink-0"
        style={{ width: size, height: size }}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-c5)"
            strokeWidth={1}
          />
          {segments.map((segment, index) => {
            const fraction = (segment.value / total) * progress;
            const dash = circumference * fraction;
            // 2px gap between segments so they read as separate inlays.
            const visibleDash = Math.max(0, dash - 2);
            const startOffset = offsetAccumulator;
            offsetAccumulator += dash;
            const isDimmed = hovered !== null && hovered !== index;
            return (
              <circle
                key={segment.label}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={`var(${segment.colorVar})`}
                strokeWidth={hovered === index ? stroke + 4 : stroke}
                strokeDasharray={`${visibleDash} ${circumference - visibleDash}`}
                strokeDashoffset={-startOffset}
                transform={`rotate(-90 ${size / 2} ${size / 2})`}
                onMouseEnter={() => setHovered(index)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer transition-[stroke-width,opacity] duration-300"
                style={{ opacity: isDimmed ? 0.3 : 1 }}
              />
            );
          })}
        </svg>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center gap-1">
          <span className="font-display text-c1 text-3xl leading-none font-bold">
            {hovered !== null ? `${segments[hovered].value}%` : centerValue}
          </span>
          <span className="font-mono text-c3 max-w-[70%] text-center text-[8px] tracking-[0.18em] uppercase">
            {hovered !== null ? segments[hovered].label : centerLabel}
          </span>
        </div>
      </div>

      <ul className="flex flex-col gap-2.5">
        {segments.map((segment, index) => (
          <li key={segment.label}>
            <button
              type="button"
              onMouseEnter={() => setHovered(index)}
              onMouseLeave={() => setHovered(null)}
              className={cn(
                "flex items-center gap-2.5 text-left transition-opacity duration-300",
                hovered !== null && hovered !== index && "opacity-40",
              )}
            >
              <span
                className="h-2 w-2 shrink-0 rounded-full"
                style={{ background: `var(${segment.colorVar})` }}
              />
              <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
                {segment.label}
              </span>
              <span className="font-display text-c1 ml-1 text-xs font-bold">
                {segment.value}%
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
