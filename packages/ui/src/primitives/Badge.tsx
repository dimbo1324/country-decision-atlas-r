"use client";

import type { ReactNode } from "react";
import { cn } from "../lib/cn";

export type BadgeVariant =
  | "default"
  | "positive"
  | "negative"
  | "warning"
  | "critical"
  | "info"
  | "trust";

const VARIANT_CLASSES: Record<BadgeVariant, string> = {
  default: "border-warm text-c3",
  positive: "border-sage2/60 text-sage3",
  negative: "border-terra2/60 text-terra3",
  warning: "border-gold2/60 text-gold3",
  critical: "border-terra bg-terra/10 text-terra3",
  info: "border-blue2/60 text-blue3",
  trust: "border-sage2/60 text-sage3",
};

interface BadgeProps {
  children: ReactNode;
  variant?: BadgeVariant;
  title?: string;
}

export function Badge({ children, variant = "default", title }: BadgeProps) {
  return (
    <span
      title={title}
      className={cn(
        "font-mono inline-flex items-center gap-1.5 border px-2 py-1 text-[9px] tracking-[0.15em] uppercase",
        VARIANT_CLASSES[variant],
      )}
    >
      {children}
    </span>
  );
}
