"use client";

import type { ReactNode } from "react";
import { cn } from "../lib/cn";

interface FieldProps {
  children: ReactNode;
  className?: string;
}

/** Form-field shell: label in mono uppercase → control → hint/error below.
 * Framework-agnostic — pair the control with React Hook Form's `register()`
 * or a Controller render prop; this component only owns the layout/skin. */
export function Field({ children, className }: FieldProps) {
  return <div className={cn("flex flex-col gap-1.5", className)}>{children}</div>;
}

export function FieldLabel({
  children,
  htmlFor,
  className,
}: {
  children: ReactNode;
  htmlFor?: string;
  className?: string;
}) {
  return (
    <label
      htmlFor={htmlFor}
      className={cn(
        "font-mono text-c3 text-[10px] tracking-[0.2em] uppercase",
        className,
      )}
    >
      {children}
    </label>
  );
}

export function FieldHint({ children }: { children: ReactNode }) {
  return <span className="text-c4 text-xs leading-relaxed">{children}</span>;
}

export function FieldError({ children }: { children?: ReactNode }) {
  if (!children) return null;
  return (
    <span
      role="alert"
      className="font-quote text-terra3 text-xs italic"
    >
      {children}
    </span>
  );
}
