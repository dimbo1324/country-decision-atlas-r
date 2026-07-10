import { type ReactNode, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Maximize2, Minimize2 } from "lucide-react";
import { cn } from "@/lib/cn";

interface ChartFrameProps {
  title: string;
  live?: boolean;
  children: ReactNode;
  className?: string;
  expandable?: boolean;
}

function FrameHeader({
  title,
  live,
  expanded,
  expandable,
  onToggle,
}: {
  title: string;
  live: boolean;
  expanded: boolean;
  expandable: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="mb-4 flex items-center justify-between gap-4">
      <span className="font-mono text-c3 truncate text-[10px] tracking-[0.2em] uppercase">
        {title}
      </span>
      <div className="flex shrink-0 items-center gap-4">
        {live && (
          <span className="font-mono text-gold3 inline-flex items-center gap-1.5 text-[10px] tracking-[0.2em] uppercase">
            <span className="bg-gold h-1.5 w-1.5 animate-pulse rounded-full" />
            Онлайн
          </span>
        )}
        {expandable && (
          <button
            type="button"
            onClick={onToggle}
            aria-label={expanded ? "Свернуть график" : "Развернуть график"}
            className="border-warm text-c3 hover:border-warm-hi hover:text-c1 flex h-7 w-7 shrink-0 items-center justify-center border transition-colors duration-300"
          >
            {expanded ? (
              <Minimize2
                width={13}
                height={13}
                strokeWidth={1.5}
              />
            ) : (
              <Maximize2
                width={13}
                height={13}
                strokeWidth={1.5}
              />
            )}
          </button>
        )}
      </div>
    </div>
  );
}

export function ChartFrame({
  title,
  live = true,
  children,
  className,
  expandable = true,
}: ChartFrameProps) {
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!expanded) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setExpanded(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [expanded]);

  return (
    <div
      className={cn(
        "bg-bg3 border-warm flex flex-1 flex-col overflow-hidden border p-5",
        className,
      )}
    >
      <FrameHeader
        title={title}
        live={live}
        expanded={false}
        expandable={expandable}
        onToggle={() => setExpanded(true)}
      />
      <div className="relative min-h-0 flex-1">
        {expanded ? (
          <div className="font-mono text-c4 flex h-full items-center justify-center text-center text-[10px] tracking-[0.2em] uppercase">
            График развёрнут
          </div>
        ) : (
          children
        )}
      </div>

      {expanded &&
        createPortal(
          <div
            className="fixed inset-0 z-[70] flex bg-black/70 p-4 backdrop-blur-sm sm:p-8"
            onClick={() => setExpanded(false)}
          >
            <div
              className="bg-bg3 border-warm relative flex h-full w-full flex-col border p-6"
              onClick={(event) => event.stopPropagation()}
            >
              <FrameHeader
                title={title}
                live={live}
                expanded
                expandable
                onToggle={() => setExpanded(false)}
              />
              <div className="relative min-h-0 flex-1">{children}</div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}

export function MetricStat({
  value,
  label,
}: {
  value: ReactNode;
  label: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-display text-gold3 text-3xl font-bold">
        {value}
      </span>
      <span className="font-mono text-c3 text-[10px] tracking-[0.15em] uppercase">
        {label}
      </span>
    </div>
  );
}
