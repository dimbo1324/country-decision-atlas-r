import type { SlideDef } from "@/lib/types";

interface MobileStackProps {
  slides: SlideDef[];
}

export function MobileStack({ slides }: MobileStackProps) {
  return (
    <div className="hidden h-full snap-x snap-mandatory overflow-x-auto max-[820px]:flex">
      {slides.map((slide) => (
        <div
          key={slide.id}
          className="h-full w-screen shrink-0 snap-start overflow-y-auto"
        >
          {slide.content}
        </div>
      ))}
    </div>
  );
}
