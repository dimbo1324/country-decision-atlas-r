"use client";

import { useRef, type KeyboardEvent } from "react";
import { cn } from "../lib/cn";
import { ACCENTS, type Accent } from "../lib/accents";

export interface RadioCardOption {
  value: string;
  label: string;
  description?: string;
}

interface RadioCardsProps {
  name: string;
  options: RadioCardOption[];
  value: string;
  onChange: (value: string) => void;
  accent?: Accent;
  className?: string;
  ariaLabel?: string;
}

export function RadioCards({
  name,
  options,
  value,
  onChange,
  accent = "gold",
  className,
  ariaLabel,
}: RadioCardsProps) {
  const accentClasses = ACCENTS[accent];
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const selectedIndex = options.findIndex((option) => option.value === value);
  const focusableIndex = selectedIndex === -1 ? 0 : selectedIndex;

  function focusAndSelect(nextIndex: number) {
    const option = options[nextIndex];
    if (!option) return;
    onChange(option.value);
    buttonRefs.current[nextIndex]?.focus();
  }

  /** ARIA radiogroup pattern: arrow keys move focus *and* selection
   * together between options, matching native `<input type="radio">`
   * behavior -- Tab only ever stops once on the group (roving tabindex
   * below), not once per option. */
  function handleKeyDown(
    event: KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) {
    switch (event.key) {
      case "ArrowRight":
      case "ArrowDown":
        event.preventDefault();
        focusAndSelect((index + 1) % options.length);
        break;
      case "ArrowLeft":
      case "ArrowUp":
        event.preventDefault();
        focusAndSelect((index - 1 + options.length) % options.length);
        break;
      case "Home":
        event.preventDefault();
        focusAndSelect(0);
        break;
      case "End":
        event.preventDefault();
        focusAndSelect(options.length - 1);
        break;
    }
  }

  return (
    <div
      role="radiogroup"
      aria-label={ariaLabel}
      className={cn("grid grid-cols-1 gap-3 sm:grid-cols-2", className)}
    >
      {options.map((option, index) => {
        const checked = option.value === value;
        return (
          <button
            key={option.value}
            ref={(el) => {
              buttonRefs.current[index] = el;
            }}
            type="button"
            role="radio"
            aria-checked={checked}
            tabIndex={index === focusableIndex ? 0 : -1}
            onKeyDown={(event) => handleKeyDown(event, index)}
            name={name}
            data-testid={`${name}-option-${option.value}`}
            onClick={() => onChange(option.value)}
            className={cn(
              "bg-bg2 flex flex-col gap-1 border p-4 text-left transition-colors duration-300",
              checked
                ? cn("border-transparent", accentClasses.bg + "/10")
                : "border-warm",
              checked && accentClasses.border,
            )}
            style={
              checked
                ? { boxShadow: `inset 0 0 0 1px var(--color-${accent})` }
                : undefined
            }
          >
            <span
              className={cn(
                "font-body text-sm font-semibold",
                checked ? accentClasses.textBright : "text-c1",
              )}
            >
              {option.label}
            </span>
            {option.description && (
              <span className="text-c3 text-xs leading-relaxed">
                {option.description}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
