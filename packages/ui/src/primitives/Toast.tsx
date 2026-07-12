"use client";

import { Toaster as SonnerToaster } from "sonner";

export { toast } from "sonner";

/** Sonner, restyled to the archive palette via its `classNames` theming API
 * (no separate CSS file to keep in sync). */
export function Toaster() {
  return (
    <SonnerToaster
      theme="dark"
      position="bottom-right"
      toastOptions={{
        unstyled: true,
        classNames: {
          toast:
            "bg-bg4 border-warm-hi border flex items-start gap-3 p-4 w-full font-body text-sm shadow-[0_16px_40px_rgb(0_0_0/0.45)]",
          title: "text-c1 font-semibold",
          description: "text-c3 text-xs mt-1",
          actionButton:
            "font-mono border-gold2 text-gold3 border px-3 py-1.5 text-[9px] tracking-[0.2em] uppercase",
          cancelButton:
            "font-mono text-c3 border-warm border px-3 py-1.5 text-[9px] tracking-[0.2em] uppercase",
          success: "border-l-2 border-l-[var(--color-sage)]",
          error: "border-l-2 border-l-[var(--color-terra)]",
          warning: "border-l-2 border-l-[var(--color-gold)]",
          info: "border-l-2 border-l-[var(--color-blue)]",
        },
      }}
    />
  );
}
