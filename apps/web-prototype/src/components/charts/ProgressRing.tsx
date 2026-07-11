import { useEffect, useRef, useState } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface ProgressRingProps {
  /** 0..100 */
  value: number;
  label: string;
  size?: number;
  colorVar?: string;
  active: boolean;
  suffix?: string;
}

export function ProgressRing({
  value,
  label,
  size = 168,
  colorVar = "--color-gold",
  active,
  suffix = "",
}: ProgressRingProps) {
  const reducedMotion = useReducedMotion();
  const [armed, setArmed] = useState(false);
  const [display, setDisplay] = useState(0);
  const startedRef = useRef(false);

  const stroke = 3;
  const radius = size / 2 - stroke * 2;
  const circumference = 2 * Math.PI * radius;
  const shownValue = armed ? value : 0;

  // Arm the dashoffset transition one frame after activation so the ring
  // visibly fills from zero (CSS transitions need a rendered "from" state),
  // and run the counter with the same ease-out cubic as every number here.
  useEffect(() => {
    if (!active || startedRef.current) return;
    startedRef.current = true;
    if (reducedMotion) {
      setArmed(true);
      setDisplay(value);
      return;
    }
    const raf = requestAnimationFrame(() => setArmed(true));
    const start = performance.now();
    const durationMs = 1400;
    const step = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      setDisplay(Math.round(value * (1 - (1 - progress) ** 3)));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [active, reducedMotion, value]);

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="absolute inset-0"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-c5)"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`var(${colorVar})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - shownValue / 100)}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{
            transition: reducedMotion
              ? "none"
              : "stroke-dashoffset 1.4s var(--ease-arrive)",
          }}
        />
      </svg>
      <div className="flex flex-col items-center gap-1">
        <span
          className="font-display text-4xl leading-none font-bold"
          style={{ color: `var(${colorVar})` }}
        >
          {display}
          {suffix}
        </span>
        <span className="font-mono text-c3 max-w-[80%] text-center text-[9px] tracking-[0.2em] uppercase">
          {label}
        </span>
      </div>
    </div>
  );
}
