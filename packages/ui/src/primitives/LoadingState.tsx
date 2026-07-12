"use client";

import { cn } from "../lib/cn";

interface LoadingStateProps {
  message: string;
  className?: string;
}

export function LoadingState({ message, className }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 p-8 text-center",
        className,
      )}
    >
      <span
        className="flex gap-1.5"
        aria-hidden="true"
      >
        {[0, 1, 2].map((index) => (
          <span
            key={index}
            className="bg-gold2 h-1.5 w-1.5 animate-pulse rounded-full"
            style={{ animationDelay: `${index * 0.18}s` }}
          />
        ))}
      </span>
      <p className="text-c3 font-mono text-[10px] tracking-[0.2em] uppercase">{message}</p>
    </div>
  );
}
