"use client";

import type { ReactNode } from "react";
import { cn } from "../lib/cn";

interface ErrorStateProps {
  title: ReactNode;
  code?: string;
  message: ReactNode;
  action?: ReactNode;
  className?: string;
}

/** Presentational shell only — callers decide what counts as an error
 * (backend-down detection, API error-envelope parsing, etc.) and pass the
 * already-resolved title/code/message/action through. */
export function ErrorState({
  title,
  code,
  message,
  action,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn(
        "border-terra2/60 bg-bg3 flex flex-col items-center gap-2 border p-8 text-center",
        className,
      )}
    >
      <strong className="font-display text-c1 text-lg font-semibold">
        {title}
      </strong>
      {code && (
        <span className="font-mono text-terra3 text-[9px] tracking-[0.2em] uppercase">
          {code}
        </span>
      )}
      <span className="text-c3 max-w-md text-sm leading-relaxed">
        {message}
      </span>
      {action}
    </div>
  );
}
