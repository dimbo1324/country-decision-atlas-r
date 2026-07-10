import type { CSSProperties, ReactNode } from "react";
import { cn } from "@/lib/cn";
import type { Accent } from "@/lib/accents";

interface CardProps {
  accent?: Accent;
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  interactive?: boolean;
}

export function Card({
  accent = "gold",
  children,
  onClick,
  className,
  interactive = true,
}: CardProps) {
  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={
        {
          "--glow-1": `var(--color-${accent}2)`,
          "--glow-2": `var(--color-${accent})`,
          "--glow-3": `var(--color-${accent}3)`,
        } as CSSProperties
      }
      className={cn(
        // Static box: no transform, no size change. Hovering only (a) reads
        // as a thicker border via an inset shadow ring — box-shadow never
        // participates in layout, so nothing reflows — and (b) traces a
        // laser sweep strictly around the perimeter via the .card-glow
        // pseudo-elements in index.css, clipped by overflow-hidden so
        // nothing bleeds past the card edge into the surrounding space.
        "bg-bg2 border-warm relative overflow-hidden border p-6 transition-[box-shadow,border-color] duration-300",
        onClick && "cursor-pointer",
        interactive &&
          "card-glow hover:border-transparent hover:shadow-[inset_0_0_0_1px_var(--glow-2)]",
        className,
      )}
    >
      {children}
    </div>
  );
}
