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
        "flex h-full w-full flex-col justify-center gap-10 px-10 pt-24 pb-16 sm:px-16 lg:px-24",
        className,
      )}
    >
      {children}
    </div>
  );
}
