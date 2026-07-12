"use client";

import { ArrowDown, ArrowUp, Info } from "lucide-react";
import { cn } from "../lib/cn";

export interface TimelineEvent {
  id: string;
  date: string;
  impact: "up" | "down" | "info";
  impactLabel: string;
  title: string;
  source: string;
}

interface TimelineListProps {
  events: TimelineEvent[];
  className?: string;
}

const IMPACT_STYLES: Record<
  TimelineEvent["impact"],
  { icon: typeof ArrowUp; frame: string; text: string }
> = {
  up: {
    icon: ArrowUp,
    frame: "border-sage2 text-sage",
    text: "text-sage3",
  },
  down: {
    icon: ArrowDown,
    frame: "border-terra2 text-terra",
    text: "text-terra3",
  },
  info: {
    icon: Info,
    frame: "border-blue2 text-blue",
    text: "text-blue3",
  },
};

/** The mockup's "What changed" feed: dated rows with impact + source. */
export function TimelineList({ events, className }: TimelineListProps) {
  return (
    <ul className={cn("flex flex-col", className)}>
      {events.map((event) => {
        const impact = IMPACT_STYLES[event.impact];
        const ImpactIcon = impact.icon;
        return (
          <li
            key={event.id}
            className="group border-warm relative grid grid-cols-[auto_1fr_auto] items-center gap-4 border-b py-3.5"
          >
            <span className="font-mono text-c4 w-[74px] shrink-0 text-[9px] tracking-[0.12em]">
              {event.date}
            </span>
            <span className="flex min-w-0 items-center gap-3">
              <span
                className={cn(
                  "flex h-7 w-7 shrink-0 items-center justify-center border",
                  impact.frame,
                )}
              >
                <ImpactIcon
                  width={13}
                  height={13}
                  strokeWidth={1.5}
                />
              </span>
              <span className="flex min-w-0 flex-col">
                <strong className="text-c2 group-hover:text-c1 truncate text-sm font-semibold transition-colors duration-300">
                  {event.title}
                </strong>
                <span className={cn("truncate text-xs", impact.text)}>
                  {event.impactLabel}
                </span>
              </span>
            </span>
            <span className="font-mono text-c4 shrink-0 text-[8px] tracking-[0.15em] uppercase">
              {event.source}
            </span>
            {/* Signature table-row hover: underline sweeps in from the left. */}
            <span className="bg-gold2/70 absolute right-0 bottom-0 left-0 h-px origin-left scale-x-0 transition-transform duration-500 group-hover:scale-x-100" />
          </li>
        );
      })}
    </ul>
  );
}
