"use client";

import { useReducedMotion } from "../hooks/useReducedMotion";

interface SignalTickerProps {
  items: string[];
  /** Full loop duration; longer = slower crawl. */
  durationSec?: number;
}

/** Archive-wire ticker: one seamless crawling line of the latest signals.
 * The track holds the item list twice and translates by exactly -50%, so
 * the loop point is invisible. Pauses on hover; with reduced motion it
 * degrades to a static (scrollable) strip. */
export function SignalTicker({ items, durationSec = 40 }: SignalTickerProps) {
  const reducedMotion = useReducedMotion();

  const renderItems = (ariaHidden: boolean) =>
    items.map((item, index) => (
      <span
        key={`${ariaHidden ? "b" : "a"}-${index}`}
        aria-hidden={ariaHidden}
        className="font-mono text-c3 inline-flex shrink-0 items-center gap-3 text-[10px] tracking-[0.15em] uppercase"
      >
        <span className="bg-gold2 inline-block h-1 w-1 shrink-0 rounded-full" />
        {item}
      </span>
    ));

  if (reducedMotion) {
    return (
      <div className="border-warm bg-bg3 scrollbar-thin flex gap-8 overflow-x-auto border-y px-4 py-2.5">
        {renderItems(false)}
      </div>
    );
  }

  return (
    <div className="group border-warm bg-bg3 relative overflow-hidden border-y py-2.5">
      <div
        className="flex w-max gap-8 pr-8 will-change-transform group-hover:[animation-play-state:paused]"
        style={{
          animation: `ticker-crawl ${durationSec}s linear infinite`,
        }}
      >
        {renderItems(false)}
        {renderItems(true)}
      </div>
      {/* Soft fade at both edges so items enter/exit like under a scanner. */}
      <div className="from-bg3 pointer-events-none absolute inset-y-0 left-0 w-16 bg-gradient-to-r to-transparent" />
      <div className="from-bg3 pointer-events-none absolute inset-y-0 right-0 w-16 bg-gradient-to-l to-transparent" />
    </div>
  );
}
