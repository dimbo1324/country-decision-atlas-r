import { Compass, LibraryBig } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/Button";
import type { SlideDef } from "@/lib/types";

interface TopBarProps {
  slides: SlideDef[];
  activeIndex: number;
  onNavigate: (index: number) => void;
  isRunning: boolean;
  onRunAnalysis: () => void;
  onOpenLibrary: () => void;
}

export function TopBar({
  slides,
  activeIndex,
  onNavigate,
  isRunning,
  onRunAnalysis,
  onOpenLibrary,
}: TopBarProps) {
  return (
    <header className="border-warm fixed inset-x-0 top-0 z-50 flex items-center justify-between gap-4 border-b bg-black/40 px-6 py-4 backdrop-blur-md">
      <div className="flex shrink-0 items-center gap-3">
        <span className="border-gold2 text-gold flex h-8 w-8 items-center justify-center border">
          <Compass
            width={16}
            height={16}
            strokeWidth={1.5}
          />
        </span>
        <span className="font-display text-sm font-bold tracking-[0.3em] uppercase max-[1240px]:hidden">
          CountryAtlas
        </span>
      </div>

      <nav className="flex items-center max-[1080px]:hidden">
        {slides.map((slide, slideIndex) => (
          <button
            key={slide.id}
            onClick={() => onNavigate(slideIndex)}
            className={cn(
              "font-mono relative px-2.5 py-2 text-[11px] tracking-[0.14em] uppercase transition-colors duration-300",
              slideIndex === activeIndex ? "text-c1" : "text-c3 hover:text-c1",
            )}
          >
            {slide.navLabel}
            <span
              className={cn(
                "bg-gold absolute right-2.5 bottom-1 left-2.5 h-px origin-left transition-transform duration-300",
                slideIndex === activeIndex ? "scale-x-100" : "scale-x-0",
              )}
            />
          </button>
        ))}
      </nav>

      <div className="flex shrink-0 items-center gap-2.5">
        <button
          type="button"
          onClick={onOpenLibrary}
          className="group border-warm text-c2 hover:border-gold2 hover:text-gold3 font-mono inline-flex items-center gap-2 border px-3.5 py-3 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          <LibraryBig
            width={13}
            height={13}
            strokeWidth={1.5}
            className="transition-transform duration-300 group-hover:scale-115"
          />
          <span className="max-[1240px]:hidden">Библиотека</span>
        </button>
        <Button
          variant="primary"
          onClick={onRunAnalysis}
          disabled={isRunning}
          aria-live="polite"
          className={cn(
            "w-[176px] shrink-0",
            isRunning && "cursor-wait opacity-60",
          )}
        >
          {isRunning ? "Пересчёт…" : "Запустить анализ"}
        </Button>
      </div>
    </header>
  );
}
