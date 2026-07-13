"use client";

import { ProgressRing } from "../charts/ProgressRing";

interface AnalysisOverlayProps {
  active: boolean;
  label?: string;
}

/** Full-screen "recalculating" overlay shown while a decision run/compare
 * mutation is in flight — the fixed backdrop plus a live-mode ProgressRing
 * standing in for progress (the underlying request has no real progress
 * signal, so the ring communicates "working", not a literal percentage). */
export function AnalysisOverlay({
  active,
  label = "Пересчёт индексов",
}: AnalysisOverlayProps) {
  if (!active) return null;

  return (
    <div
      className="fixed inset-0 z-[80] flex items-center justify-center bg-black/70 backdrop-blur-sm transition-opacity duration-300"
      role="status"
      aria-live="polite"
      data-testid="analysis-overlay"
    >
      <div className="flex flex-col items-center gap-6">
        <ProgressRing
          value={72}
          label=""
          size={104}
          accent="gold"
          active={active}
          mode="live"
        />
        <span className="font-mono text-c2 text-[11px] tracking-[0.25em] uppercase">
          {label}
        </span>
      </div>
    </div>
  );
}
