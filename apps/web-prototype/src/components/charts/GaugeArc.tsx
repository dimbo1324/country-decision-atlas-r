import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface GaugeArcProps {
  /** 0..100 */
  value: number;
  label: string;
  valueLabel?: string;
  active: boolean;
  colorVar?: string;
  width?: number;
}

const START_ANGLE = Math.PI;
const SWEEP = Math.PI;

function polar(cx: number, cy: number, r: number, angle: number) {
  return { x: cx + Math.cos(angle) * r, y: cy + Math.sin(angle) * r };
}

function arcPath(cx: number, cy: number, r: number, fraction: number): string {
  const end = START_ANGLE + SWEEP * Math.max(0.001, fraction);
  const from = polar(cx, cy, r, START_ANGLE);
  const to = polar(cx, cy, r, end);
  const largeArc = SWEEP * fraction > Math.PI ? 1 : 0;
  return `M ${from.x} ${from.y} A ${r} ${r} 0 ${largeArc} 1 ${to.x} ${to.y}`;
}

export function GaugeArc({
  value,
  label,
  valueLabel,
  active,
  colorVar = "--color-terra",
  width = 220,
}: GaugeArcProps) {
  const reducedMotion = useReducedMotion();
  const [progress, setProgress] = useState(0);
  const startedRef = useRef(false);

  const height = width * 0.62;
  const cx = width / 2;
  const cy = height * 0.86;
  const radius = width * 0.38;

  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (reducedMotion) {
      setProgress(value / 100);
      return;
    }
    const start = performance.now();
    const durationMs = 1400;
    const step = (now: number) => {
      const p = Math.min(1, (now - start) / durationMs);
      setProgress((value / 100) * (1 - (1 - p) ** 3));
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [active, reducedMotion, value]);

  const needleAngle = START_ANGLE + SWEEP * progress;
  const needleTip = polar(cx, cy, radius - 10, needleAngle);

  return (
    <div
      className="flex flex-col items-center"
      style={{ width }}
    >
      <svg
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Track with tick marks: an engraved dial, not a plain arc. */}
        <path
          d={arcPath(cx, cy, radius, 1)}
          fill="none"
          stroke="var(--color-c5)"
          strokeWidth={3}
          strokeLinecap="round"
        />
        {Array.from({ length: 11 }, (_, i) => {
          const angle = START_ANGLE + (SWEEP * i) / 10;
          const outer = polar(cx, cy, radius + 7, angle);
          const inner = polar(cx, cy, radius + (i % 5 === 0 ? 1 : 4), angle);
          return (
            <line
              key={i}
              x1={inner.x}
              y1={inner.y}
              x2={outer.x}
              y2={outer.y}
              stroke="var(--color-c4)"
              strokeWidth={1}
            />
          );
        })}
        <path
          d={arcPath(cx, cy, radius, progress)}
          fill="none"
          stroke={`var(${colorVar})`}
          strokeWidth={3}
          strokeLinecap="round"
        />
        <line
          x1={cx}
          y1={cy}
          x2={needleTip.x}
          y2={needleTip.y}
          stroke="var(--color-c1)"
          strokeWidth={1.5}
        />
        <circle
          cx={cx}
          cy={cy}
          r={3.5}
          fill={`var(${colorVar})`}
        />
      </svg>
      <div className="-mt-3 flex flex-col items-center gap-1">
        <span
          className="font-display text-3xl leading-none font-bold"
          style={{ color: `var(${colorVar})` }}
        >
          {valueLabel ?? Math.round(progress * 100)}
        </span>
        <span className="font-mono text-c3 text-[9px] tracking-[0.2em] uppercase">
          {label}
        </span>
      </div>
    </div>
  );
}
