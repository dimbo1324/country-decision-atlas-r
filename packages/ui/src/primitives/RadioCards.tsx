"use client";

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
}

export function RadioCards({
  name,
  options,
  value,
  onChange,
  accent = "gold",
  className,
}: RadioCardsProps) {
  const accentClasses = ACCENTS[accent];
  return (
    <div
      role="radiogroup"
      className={cn("grid grid-cols-1 gap-3 sm:grid-cols-2", className)}
    >
      {options.map((option) => {
        const checked = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={checked}
            name={name}
            onClick={() => onChange(option.value)}
            className={cn(
              "bg-bg2 flex flex-col gap-1 border p-4 text-left transition-colors duration-300",
              checked ? cn("border-transparent", accentClasses.bg + "/10") : "border-warm",
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
              <span className="text-c3 text-xs leading-relaxed">{option.description}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}
