"use client";

import type { ReactNode, TouchEvent } from "react";
import { useEffect, useRef, useState } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { cn } from "../lib/cn";
import { ACCENTS, type Accent } from "../lib/accents";

export interface DeckSlide {
  id: string;
  navLabel: string;
  accent: Accent;
  content: ReactNode;
}

interface HorizontalPagerProps {
  slides: DeckSlide[];
  index: number;
  onIndexChange: (index: number) => void;
  className?: string;
}

const SWIPE_THRESHOLD_PX = 60;

type HoverSide = "prev" | "next" | null;

function NavArrow({
  direction,
  onClick,
  disabled,
  label,
  targetLabel,
  hovered,
  onHoverChange,
  testId,
}: {
  direction: "prev" | "next";
  onClick: () => void;
  disabled: boolean;
  label: string;
  targetLabel?: string;
  hovered: boolean;
  onHoverChange: (hovered: boolean) => void;
  testId: string;
}) {
  const Icon = direction === "prev" ? ArrowLeft : ArrowRight;
  return (
    <div className="group relative flex items-center">
      <button
        type="button"
        onClick={onClick}
        onMouseEnter={() => onHoverChange(true)}
        onMouseLeave={() => onHoverChange(false)}
        onFocus={() => onHoverChange(true)}
        onBlur={() => onHoverChange(false)}
        disabled={disabled}
        aria-label={label}
        data-testid={testId}
        className={cn(
          "border-c5/60 text-c4 flex h-11 w-11 shrink-0 items-center justify-center border bg-black/10 backdrop-blur-sm transition-all duration-300",
          "hover:border-gold2 hover:text-gold3 hover:bg-black/50",
          "disabled:pointer-events-none disabled:opacity-0",
        )}
      >
        <Icon
          width={18}
          height={18}
          strokeWidth={1.5}
        />
      </button>
      {targetLabel && (
        <span
          className={cn(
            "border-warm bg-bg4 text-c2 pointer-events-none absolute bottom-full left-1/2 mb-3 -translate-x-1/2 border px-3 py-1.5 font-mono text-[9px] whitespace-nowrap uppercase transition-opacity duration-300",
            "tracking-[0.15em]",
            hovered ? "opacity-100" : "opacity-0",
          )}
        >
          {direction === "prev" ? "Назад" : "Далее"} · {targetLabel}
        </span>
      )}
    </div>
  );
}

/** Embedded (not full-viewport) horizontal deck: click/dot/arrow and touch
 * swipe navigation only. Deliberately does not port the prototype's global
 * wheel/keydown hijacking — those assume the pager owns the entire viewport
 * with nothing else to scroll; here the deck sits mid-page above a footer
 * and quick links, so global wheel/arrow-key capture would fight normal
 * page scrolling and keyboard navigation elsewhere on the page. Visible only
 * at >820px — `MobileStack` takes over below that via a sibling component. */
export function HorizontalPager({
  slides,
  index,
  onIndexChange,
  className,
}: HorizontalPagerProps) {
  const isFirst = index === 0;
  const isLast = index === slides.length - 1;
  const goPrev = () => onIndexChange(Math.max(0, index - 1));
  const goNext = () => onIndexChange(Math.min(slides.length - 1, index + 1));
  const touchStartX = useRef<number | null>(null);
  const [hoverSide, setHoverSide] = useState<HoverSide>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(0);

  // Measured in pixels rather than left as a CSS percentage-of-percentage
  // (row width 100*n%, translateX -100/n% of that) -- the two compose
  // unreliably in practice, resolving to an identity transform in some
  // engines. Pixels sidestep that entirely. Initial width is read
  // synchronously (not only from ResizeObserver's first callback, which
  // some environments never deliver) so the pager is correctly positioned
  // from the first render; ResizeObserver only handles later resizes, and
  // that path is debounced, matching this codebase's other resize-driven
  // shell components.
  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;
    setContainerWidth(node.getBoundingClientRect().width);

    let resizeTimer: ReturnType<typeof setTimeout> | undefined;
    const observer = new ResizeObserver((entries) => {
      const width = entries[0]?.contentRect.width;
      if (!width) return;
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => setContainerWidth(width), 150);
    });
    observer.observe(node);
    return () => {
      clearTimeout(resizeTimer);
      observer.disconnect();
    };
  }, []);

  const handleTouchStart = (event: TouchEvent<HTMLDivElement>) => {
    touchStartX.current = event.touches[0]?.clientX ?? null;
  };

  const handleTouchEnd = (event: TouchEvent<HTMLDivElement>) => {
    if (touchStartX.current === null) return;
    const endX = event.changedTouches[0]?.clientX ?? touchStartX.current;
    const delta = touchStartX.current - endX;
    if (Math.abs(delta) > SWIPE_THRESHOLD_PX) {
      if (delta > 0) onIndexChange(Math.min(slides.length - 1, index + 1));
      else onIndexChange(Math.max(0, index - 1));
    }
    touchStartX.current = null;
  };

  const current = slides[index];
  const accentClasses = current ? ACCENTS[current.accent] : ACCENTS.gold;

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative hidden h-full w-full overflow-hidden min-[821px]:block",
        className,
      )}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div
        className="flex h-full transition-transform duration-500 [transition-timing-function:var(--ease-arrive,ease)] motion-reduce:transition-none"
        style={{
          width: containerWidth
            ? `${slides.length * containerWidth}px`
            : `${slides.length * 100}%`,
          transform: containerWidth
            ? `translateX(-${index * containerWidth}px)`
            : `translateX(-${index * (100 / slides.length)}%)`,
        }}
      >
        {slides.map((slide) => (
          <div
            key={slide.id}
            className="h-full shrink-0 overflow-y-auto px-1 pb-16"
            style={{
              width: containerWidth
                ? `${containerWidth}px`
                : `${100 / slides.length}%`,
            }}
            // `inert` (not just aria-hidden): links inside off-screen
            // slides must also leave the tab order, otherwise keyboard
            // focus lands in invisible content.
            inert={slide.id !== current?.id}
            data-testid={`pager-slide-${slide.id}`}
          >
            {slide.content}
          </div>
        ))}
      </div>

      <div className="absolute inset-x-0 bottom-2 z-10 flex items-center justify-center gap-8">
        <NavArrow
          direction="prev"
          onClick={goPrev}
          disabled={isFirst}
          label="Предыдущий блок"
          targetLabel={isFirst ? undefined : slides[index - 1]?.navLabel}
          hovered={hoverSide === "prev"}
          onHoverChange={(hovered) => setHoverSide(hovered ? "prev" : null)}
          testId="pager-prev"
        />

        <div className="flex items-center gap-4">
          <span className="font-mono text-c3 text-[10px] tracking-[0.2em]">
            <b className="text-c1">{String(index + 1).padStart(2, "0")}</b>
            {" / "}
            {String(slides.length).padStart(2, "0")}
          </span>
          {/* A row of independently-focusable buttons in normal tab
              order, not an ARIA tablist -- roving tabindex/arrow-key
              navigation is for widgets where the items are mutually
              exclusive selections a user steps through (radiogroup,
              tablist); here each dot just jumps straight to its slide, so
              Tab-order access to all of them is the correct, simpler
              pattern (same reasoning as DecisionRunForm's step nav).
              `role="group"` + `aria-current` give it the grouping context
              and current-item semantics it was missing. */}
          <div
            role="group"
            aria-label="Слайды колоды"
            className="flex items-center gap-2"
          >
            {slides.map((slide, slideIndex) => (
              <button
                type="button"
                key={slide.id}
                onClick={() => onIndexChange(slideIndex)}
                aria-label={slide.navLabel}
                aria-current={slideIndex === index ? "true" : undefined}
                data-testid={`pager-dot-${slide.id}`}
                className={cn(
                  "h-1.5 rounded-full transition-all duration-300",
                  slideIndex === index
                    ? cn("w-6", accentClasses.bg)
                    : "border-warm-hi w-1.5 border bg-transparent hover:bg-white/10",
                )}
              />
            ))}
          </div>
        </div>

        <NavArrow
          direction="next"
          onClick={goNext}
          disabled={isLast}
          label="Следующий блок"
          targetLabel={isLast ? undefined : slides[index + 1]?.navLabel}
          hovered={hoverSide === "next"}
          onHoverChange={(hovered) => setHoverSide(hovered ? "next" : null)}
          testId="pager-next"
        />
      </div>
    </div>
  );
}
