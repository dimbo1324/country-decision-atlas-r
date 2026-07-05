import { useEffect, useState } from "react";

const RADIUS = 26;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

interface AnalysisOverlayProps {
  active: boolean;
}

export function AnalysisOverlay({ active }: AnalysisOverlayProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (!active) {
      setProgress(0);
      return;
    }
    const start = performance.now();
    let frame: number;
    const tick = (now: number) => {
      const elapsed = now - start;
      setProgress(Math.min(1, elapsed / 1500));
      if (elapsed < 1500) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [active]);

  return (
    <div
      aria-hidden={!active}
      className={
        active
          ? "pointer-events-auto fixed inset-0 z-[60] flex flex-col items-center justify-center gap-5 bg-black/55 opacity-100 backdrop-blur-sm transition-opacity duration-300"
          : "pointer-events-none fixed inset-0 z-[60] flex flex-col items-center justify-center gap-5 opacity-0 transition-opacity duration-300"
      }
    >
      <svg
        width={68}
        height={68}
        viewBox="0 0 68 68"
      >
        <circle
          cx={34}
          cy={34}
          r={RADIUS}
          fill="none"
          stroke="var(--color-c5)"
          strokeWidth={2}
        />
        <circle
          cx={34}
          cy={34}
          r={RADIUS}
          fill="none"
          stroke="var(--color-gold)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={CIRCUMFERENCE * (1 - progress)}
          transform="rotate(-90 34 34)"
          style={{ transition: "stroke-dashoffset 0.1s linear" }}
        />
      </svg>
      <div className="font-mono text-c2 text-[10px] tracking-[0.3em] uppercase">
        Пересчёт индексов
      </div>
    </div>
  );
}
