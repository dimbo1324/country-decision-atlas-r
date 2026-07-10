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
        // pb-28 (not pb-12) so the last scrolled content always clears the
        // fixed bottom-8 pager bar (32px offset + 44px arrow height) instead
        // of visually colliding with it on short viewports.
        "scrollbar-thin flex h-full w-full flex-col justify-center gap-8 overflow-y-auto px-10 pt-24 pb-28 sm:px-16 lg:px-24",
        className,
      )}
    >
      {children}
    </div>
  );
}
