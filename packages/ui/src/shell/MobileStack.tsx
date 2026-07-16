"use client";

import { cn } from "../lib/cn";
import type { DeckSlide } from "./HorizontalPager";

interface MobileStackProps {
  slides: DeckSlide[];
  className?: string;
}

/** Mobile/narrow-viewport degradation for `HorizontalPager`: native
 * horizontal scroll-snap instead of transform-driven paging, so touch
 * scrolling "just works" without custom gesture handling. Visible only at
 * <=820px, the mirror image of `HorizontalPager`'s `min-[821px]:block`. */
export function MobileStack({ slides, className }: MobileStackProps) {
  return (
    <div
      className={cn(
        "hidden h-full snap-x snap-mandatory overflow-x-auto max-[820px]:flex",
        className,
      )}
    >
      {slides.map((slide) => (
        <div
          key={slide.id}
          className="h-full w-screen shrink-0 snap-start overflow-y-auto px-1"
          data-testid={`stack-slide-${slide.id}`}
        >
          {slide.content}
        </div>
      ))}
    </div>
  );
}
