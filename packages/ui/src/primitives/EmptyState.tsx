"use client";

import type { ReactNode } from "react";
import { cn } from "../lib/cn";

interface EmptyStateProps {
  message: ReactNode;
  className?: string;
}

export function EmptyState({ message, className }: EmptyStateProps) {
  return (
    <p
      className={cn(
        "border-warm bg-bg3 text-c3 border border-dashed p-6 text-center text-sm leading-relaxed",
        className,
      )}
    >
      {message}
    </p>
  );
}
