import { useEffect, useRef } from "react";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { cn } from "@/lib/cn";
import { ACCENTS } from "@/lib/accents";
import type { SlideDef } from "@/lib/types";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface HorizontalPagerProps {
  slides: SlideDef[];
  index: number;
  onIndexChange: (index: number) => void;
}

const WHEEL_COOLDOWN_MS = 650;
const WHEEL_THRESHOLD = 12;
const SWIPE_THRESHOLD_PX = 60;

export function HorizontalPager({
  slides,
  index,
  onIndexChange,
}: HorizontalPagerProps) {
  const isFirst = index === 0;
  const isLast = index === slides.length - 1;
  const goPrev = () => onIndexChange(Math.max(0, index - 1));
  const goNext = () => onIndexChange(Math.min(slides.length - 1, index + 1));
  const reducedMotion = useReducedMotion();
  const lastWheelAt = useRef(0);
  const touchStartX = useRef<number | null>(null);

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight")
        onIndexChange(Math.min(slides.length - 1, index + 1));
      if (event.key === "ArrowLeft") onIndexChange(Math.max(0, index - 1));
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [index, onIndexChange, slides.length]);

  const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
    const delta =
      Math.abs(event.deltaX) > Math.abs(event.deltaY)
        ? event.deltaX
        : event.deltaY;
    if (Math.abs(delta) < WHEEL_THRESHOLD) return;
    const now = performance.now();
    if (now - lastWheelAt.current < WHEEL_COOLDOWN_MS) return;
    lastWheelAt.current = now;
    if (delta > 0) onIndexChange(Math.min(slides.length - 1, index + 1));
    else onIndexChange(Math.max(0, index - 1));
  };

  const handleTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    touchStartX.current = event.touches[0]?.clientX ?? null;
  };

  const handleTouchEnd = (event: React.TouchEvent<HTMLDivElement>) => {
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
      className="relative h-full w-full overflow-hidden max-[820px]:hidden"
      onWheel={handleWheel}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div
        className="flex h-full"
        style={{
          width: `${slides.length * 100}%`,
          transform: `translateX(-${index * (100 / slides.length)}%)`,
          transition: reducedMotion
            ? "none"
            : "transform 0.55s var(--ease-arrive)",
        }}
      >
        {slides.map((slide) => (
          <div
            key={slide.id}
            className="h-full shrink-0"
            style={{ width: `${100 / slides.length}%` }}
            aria-hidden={slide.id !== current?.id}
          >
            {slide.content}
          </div>
        ))}
      </div>

      <button
        onClick={goPrev}
        disabled={isFirst}
        aria-label="Предыдущий экран"
        className="border-warm text-c2 hover:border-warm-hi hover:text-c1 fixed top-1/2 left-6 z-40 flex h-11 w-11 -translate-y-1/2 items-center justify-center border bg-black/20 backdrop-blur-sm transition-all duration-300 disabled:pointer-events-none disabled:opacity-0"
      >
        <ArrowLeft
          width={18}
          height={18}
          strokeWidth={1.5}
        />
      </button>
      <button
        onClick={goNext}
        disabled={isLast}
        aria-label="Следующий экран"
        className="border-warm text-c2 hover:border-warm-hi hover:text-c1 fixed top-1/2 right-6 z-40 flex h-11 w-11 -translate-y-1/2 items-center justify-center border bg-black/20 backdrop-blur-sm transition-all duration-300 disabled:pointer-events-none disabled:opacity-0"
      >
        <ArrowRight
          width={18}
          height={18}
          strokeWidth={1.5}
        />
      </button>

      <div className="fixed right-8 bottom-8 z-40 flex items-center gap-4">
        <span className="font-mono text-c3 text-[10px] tracking-[0.2em]">
          <b className="text-c1">{String(index + 1).padStart(2, "0")}</b>
          {" / "}
          {String(slides.length).padStart(2, "0")}
        </span>
        <div className="flex items-center gap-2">
          {slides.map((slide, slideIndex) => (
            <button
              key={slide.id}
              onClick={() => onIndexChange(slideIndex)}
              aria-label={slide.navLabel}
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
    </div>
  );
}
