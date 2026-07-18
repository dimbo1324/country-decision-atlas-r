"use client";

import { cn } from "../lib/cn";

export interface FilterChipOption {
  value: string;
  label: string;
}

interface FilterChipGroupProps {
  name: string;
  label: string;
  options: FilterChipOption[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
}

/** Single-select toggle row for filter bars -- a compact, scannable
 * alternative to a native `<select>` when the option count is small
 * (country/type/confidence/impact-level style filters, not free-text or
 * long lists). Real `role="radio"` buttons, not a styled `<select>`: the
 * visible label text on each chip *is* its accessible name, so tests and
 * screen readers both identify a chip by what it says, not by an id. */
export function FilterChipGroup({
  name,
  label,
  options,
  value,
  onChange,
  className,
}: FilterChipGroupProps) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
        {label}
      </span>
      <div
        role="radiogroup"
        aria-label={label}
        className="flex flex-wrap gap-1.5"
      >
        {options.map((option) => {
          const checked = option.value === value;
          return (
            <button
              key={option.value || "__all__"}
              type="button"
              role="radio"
              aria-checked={checked}
              data-testid={`${name}-chip-${option.value || "all"}`}
              onClick={() => onChange(option.value)}
              className={cn(
                "border-warm font-mono rounded-full border px-3 py-1.5 text-[10px] tracking-[0.1em] uppercase transition-colors duration-300",
                checked
                  ? "border-gold2 bg-gold/10 text-gold3"
                  : "text-c3 hover:border-[var(--color-c3)] hover:text-c1",
              )}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
