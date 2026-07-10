import { type ReactNode, useEffect } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { cn } from "@/lib/cn";
import { ACCENTS, type Accent } from "@/lib/accents";

interface DrawerProps {
  open: boolean;
  onClose: () => void;
  accent?: Accent;
  title: ReactNode;
  eyebrow?: ReactNode;
  children: ReactNode;
}

export function Drawer({
  open,
  onClose,
  accent = "gold",
  title,
  eyebrow,
  children,
}: DrawerProps) {
  useEffect(() => {
    if (!open) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open, onClose]);

  const accentClasses = ACCENTS[accent];

  // Portalled to document.body: the pager slide this renders from lives
  // inside a `transform: translateX(...)` track, and any transformed
  // ancestor becomes the containing block for `position: fixed` descendants
  // — the drawer would be boxed into the (very wide) track instead of the
  // viewport, landing behind the top bar. Same class of bug as the chart
  // fullscreen overlay, same fix.
  return createPortal(
    <div
      aria-hidden={!open}
      className={cn(
        "fixed inset-0 z-[80] transition-opacity duration-300",
        open
          ? "pointer-events-auto opacity-100"
          : "pointer-events-none opacity-0",
      )}
    >
      <div
        onClick={onClose}
        className="absolute inset-0 bg-black/50 backdrop-blur-[3px]"
      />
      <aside
        style={{
          transitionTimingFunction: "var(--ease-spring)",
        }}
        className={cn(
          "bg-bg4 border-warm absolute top-0 right-0 flex h-full w-full max-w-md flex-col border-l transition-transform duration-500",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        <div className={cn("h-[2px] w-full shrink-0", accentClasses.bg)} />
        <div className="flex items-start justify-between p-7 pb-5">
          <div>
            {eyebrow && (
              <div className="font-mono text-c3 mb-3 text-[10px] tracking-[0.3em] uppercase">
                {eyebrow}
              </div>
            )}
            <h3 className="font-display text-c1 text-2xl font-semibold">
              {title}
            </h3>
          </div>
          <button
            onClick={onClose}
            aria-label="Закрыть"
            className="border-warm text-c2 hover:border-warm-hi hover:text-c1 flex h-9 w-9 shrink-0 items-center justify-center border transition-transform duration-300 hover:rotate-90"
          >
            <X
              width={16}
              height={16}
              strokeWidth={1.5}
            />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-7 pb-7">{children}</div>
      </aside>
    </div>,
    document.body,
  );
}
