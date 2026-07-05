import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

const ACCENT_DOT: Record<string, string> = {
  gold: "bg-gold",
  blue: "bg-blue",
  terra: "bg-terra",
  sage: "bg-sage",
  plum: "bg-plum",
};

interface KickerProps {
  children: ReactNode;
  accent?: keyof typeof ACCENT_DOT;
  className?: string;
}

export function Kicker({ children, accent = "gold", className }: KickerProps) {
  return (
    <div
      className={cn(
        "font-mono text-c3 flex items-center gap-2 text-[10px] tracking-[0.3em] uppercase",
        className,
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", ACCENT_DOT[accent])} />
      {children}
    </div>
  );
}
