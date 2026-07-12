"use client";

import { cn } from "../lib/cn";

interface SkeletonProps {
  lines?: number;
  className?: string;
}

/** Warm shimmering placeholder bars — never a cold gray block. */
export function Skeleton({ lines = 3, className }: SkeletonProps) {
  return (
    <div
      className={cn("flex flex-col gap-2.5", className)}
      aria-hidden="true"
    >
      {Array.from({ length: lines }).map((_, index) => (
        <div
          key={index}
          className="bg-c5 h-3.5 animate-pulse"
          style={{
            width: index === lines - 1 ? "60%" : "100%",
            animationDelay: `${index * 0.12}s`,
          }}
        />
      ))}
    </div>
  );
}
