"use client";

import { type ReactNode, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Maximize2, Minimize2 } from "lucide-react";
import { cn } from "../lib/cn";
import { Badge } from "./Badge";
import type { Confidence } from "../lib/confidence";

const CONFIDENCE_LABEL: Record<Confidence, string> = {
  low: "Уверенность: низкая",
  medium: "Уверенность: средняя",
  high: "Уверенность: высокая",
};

const CONFIDENCE_VARIANT: Record<
  Confidence,
  "negative" | "warning" | "positive"
> = {
  low: "negative",
  medium: "warning",
  high: "positive",
};

interface ChartFrameProps {
  title: string;
  live?: boolean;
  /** Data-transparency annotations (design-system §6): verification date
   * and confidence, shown next to the metric they describe. */
  verifiedAt?: string;
  confidence?: Confidence;
  children: ReactNode;
  className?: string;
  expandable?: boolean;
  /** Extra controls rendered in the header actions row, next to the
   * expand/collapse button — e.g. an AI explain-number trigger. */
  actions?: ReactNode;
}

function FrameHeader({
  title,
  live,
  verifiedAt,
  confidence,
  expanded,
  expandable,
  onToggle,
  actions,
}: {
  title: string;
  live: boolean;
  verifiedAt?: string;
  confidence?: Confidence;
  expanded: boolean;
  expandable: boolean;
  onToggle: () => void;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div className="flex min-w-0 flex-wrap items-center gap-3">
        <span className="font-mono text-c3 truncate text-[10px] tracking-[0.2em] uppercase">
          {title}
        </span>
        {verifiedAt && (
          <Badge
            variant="default"
            title="Дата верификации данных"
          >
            Проверено {verifiedAt}
          </Badge>
        )}
        {confidence && (
          <Badge
            variant={CONFIDENCE_VARIANT[confidence]}
            title="Уровень уверенности платформы в этом показателе"
          >
            {CONFIDENCE_LABEL[confidence]}
          </Badge>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-4">
        {live && (
          <span className="font-mono text-gold3 inline-flex items-center gap-1.5 text-[10px] tracking-[0.2em] uppercase">
            <span className="bg-gold h-1.5 w-1.5 animate-pulse rounded-full" />
            Онлайн
          </span>
        )}
        {actions}
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
  actions,
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
        actions={actions}
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
                actions={actions}
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
