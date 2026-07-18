"use client";

import type { ComponentPropsWithoutRef, ElementRef } from "react";
import { forwardRef } from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";
import { cn } from "../lib/cn";
import { ACCENTS, type Accent } from "../lib/accents";

interface SliderProps extends ComponentPropsWithoutRef<
  typeof SliderPrimitive.Root
> {
  accent?: Accent;
}

/** "Engraved scale" slider: a thin recessed track, a filled range in the
 * block's accent color, and a square-cut thumb (no rounded pill, keeps the
 * archive-instrument feel instead of reading as a generic web control). */
export const Slider = forwardRef<
  ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({ className, accent = "gold", ...rest }, ref) => {
  const accentClasses = ACCENTS[accent];
  return (
    <SliderPrimitive.Root
      ref={ref}
      className={cn(
        "relative flex w-full touch-none items-center select-none",
        className,
      )}
      {...rest}
    >
      <SliderPrimitive.Track className="bg-bg4 border-warm relative h-1 w-full grow overflow-hidden border">
        <SliderPrimitive.Range
          className={cn("absolute h-full", accentClasses.bg)}
        />
      </SliderPrimitive.Track>
      <SliderPrimitive.Thumb
        className={cn(
          "bg-bg2 block h-4 w-4 border transition-colors duration-200 focus:outline-none",
          accentClasses.border,
          accentClasses.borderHover,
        )}
        style={{ transitionTimingFunction: "var(--ease-spring)" }}
      />
    </SliderPrimitive.Root>
  );
});
Slider.displayName = "Slider";
