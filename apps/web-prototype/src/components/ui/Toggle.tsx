import { cn } from "@/lib/cn";
import { ACCENTS, type Accent } from "@/lib/accents";

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  hint?: string;
  accent?: Accent;
}

export function Toggle({
  checked,
  onChange,
  label,
  hint,
  accent = "gold",
}: ToggleProps) {
  const accentClasses = ACCENTS[accent];
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="group flex w-full items-center justify-between gap-4 text-left"
    >
      <span className="flex min-w-0 flex-col gap-0.5">
        <span
          className={cn(
            "font-body text-sm transition-colors duration-300",
            checked ? "text-c1" : "text-c2 group-hover:text-c1",
          )}
        >
          {label}
        </span>
        {hint && (
          <span className="font-mono text-c4 text-[8px] tracking-[0.15em] uppercase">
            {hint}
          </span>
        )}
      </span>
      <span
        className={cn(
          "relative h-5 w-10 shrink-0 border transition-colors duration-300",
          checked
            ? cn("border-transparent", accentClasses.bg)
            : "border-warm-hi bg-transparent",
        )}
      >
        <span
          className={cn(
            "absolute top-[3px] left-[3px] h-3 w-3 transition-transform duration-300",
            checked ? "translate-x-5 bg-[var(--color-bg)]" : "bg-c3",
          )}
          style={{ transitionTimingFunction: "var(--ease-spring)" }}
        />
      </span>
    </button>
  );
}
