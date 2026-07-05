import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface ChartFrameProps {
  title: string;
  live?: boolean;
  children: ReactNode;
  className?: string;
}

export function ChartFrame({
  title,
  live = true,
  children,
  className,
}: ChartFrameProps) {
  return (
    <div
      className={cn(
        "bg-bg3 border-warm flex flex-1 flex-col border p-5",
        className,
      )}
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
          {title}
        </span>
        {live && (
          <span className="font-mono text-gold3 inline-flex items-center gap-1.5 text-[10px] tracking-[0.2em] uppercase">
            <span className="bg-gold h-1.5 w-1.5 animate-pulse rounded-full" />
            Онлайн
          </span>
        )}
      </div>
      <div className="flex-1">{children}</div>
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
