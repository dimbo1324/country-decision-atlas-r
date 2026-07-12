"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "../lib/cn";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: "primary" | "ghost";
}

export function Button({
  children,
  variant = "primary",
  className,
  ...rest
}: ButtonProps) {
  if (variant === "ghost") {
    return (
      <button
        {...rest}
        className={cn(
          "font-mono group text-c3 hover:text-gold3 inline-flex items-center gap-2 text-[10px] tracking-[0.25em] uppercase transition-colors duration-300",
          className,
        )}
      >
        {children}
      </button>
    );
  }

  return (
    <button
      {...rest}
      className={cn(
        "group border-gold2 text-gold3 font-mono relative inline-flex items-center justify-center gap-2 overflow-hidden border px-5 py-3 text-[10px] tracking-[0.25em] uppercase",
        // No transform on :active — the ink fill animates, the box never resizes.
        "transition-[border-color,color] duration-300 active:translate-y-0",
        className,
      )}
    >
      <span
        className="bg-gold absolute inset-0 translate-y-full transition-transform duration-350 ease-out group-hover:translate-y-0"
        aria-hidden
      />
      <span className="group-hover:text-bg relative transition-colors duration-300">
        {children}
      </span>
    </button>
  );
}
