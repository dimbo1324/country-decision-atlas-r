import { Compass } from "lucide-react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/Button";
import type { SlideDef } from "@/lib/types";

interface TopBarProps {
  slides: SlideDef[];
  activeIndex: number;
  onNavigate: (index: number) => void;
  isRunning: boolean;
  onRunAnalysis: () => void;
}

export function TopBar({
  slides,
  activeIndex,
  onNavigate,
  isRunning,
  onRunAnalysis,
}: TopBarProps) {
  return (
    <header className="border-warm fixed inset-x-0 top-0 z-50 flex items-center justify-between border-b bg-black/40 px-8 py-4 backdrop-blur-md">
      <div className="flex items-center gap-3">
        <span className="border-gold2 text-gold flex h-8 w-8 items-center justify-center border">
          <Compass
            width={16}
            height={16}
            strokeWidth={1.5}
          />
        </span>
        <span className="font-display text-sm font-bold tracking-[0.3em] uppercase">
          CountryAtlas
        </span>
      </div>

      <nav className="flex items-center gap-1 max-[900px]:hidden">
        {slides.map((slide, slideIndex) => (
          <button
            key={slide.id}
            onClick={() => onNavigate(slideIndex)}
            className={cn(
              "font-mono relative px-3 py-2 text-[9px] tracking-[0.2em] uppercase transition-colors duration-300",
              slideIndex === activeIndex ? "text-c1" : "text-c3 hover:text-c1",
            )}
          >
            {slide.navLabel}
            <span
              className={cn(
                "bg-gold absolute right-3 bottom-1 left-3 h-px origin-left transition-transform duration-300",
                slideIndex === activeIndex ? "scale-x-100" : "scale-x-0",
              )}
            />
          </button>
        ))}
      </nav>

      <Button
        variant="primary"
        onClick={onRunAnalysis}
        disabled={isRunning}
        className={isRunning ? "cursor-wait opacity-60" : undefined}
      >
        {isRunning ? "Пересчёт…" : "Запустить анализ"}
      </Button>
    </header>
  );
}
