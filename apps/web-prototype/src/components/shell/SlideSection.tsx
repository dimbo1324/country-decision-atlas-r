import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

interface SlideSectionProps {
  children: ReactNode;
  className?: string;
}

export function SlideSection({ children, className }: SlideSectionProps) {
  return (
    <div
      className={cn(
        "scrollbar-thin flex h-full w-full flex-col justify-center gap-8 overflow-y-auto px-10 pt-24 pb-12 sm:px-16 lg:px-24",
        className,
      )}
    >
      {children}
    </div>
  );
}
