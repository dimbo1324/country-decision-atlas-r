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
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>{children}</div>
  );
}

export function FieldLabel({
  children,
  htmlFor,
  className,
}: {
  children: ReactNode;
  /** Required: an unlinked `<label>` is visible but not programmatically
   * associated with its control (no screen-reader name, no click-to-focus).
   * Must match the `id` of the field this label describes. */
  htmlFor: string;
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

/** Visible heading for a *group* of controls (radio group, checkbox list) --
 * deliberately not `FieldLabel`: a native `<label>` can only describe one
 * control by spec, so pairing it with a group was invalid HTML semantics
 * even before `FieldLabel.htmlFor` became required. Pair this with
 * `aria-labelledby` on the group's container (`role="group"`/
 * `role="radiogroup"`), matching text styling but as a plain heading. */
export function FieldGroupLabel({
  children,
  id,
  className,
}: {
  children: ReactNode;
  id: string;
  className?: string;
}) {
  return (
    <p
      id={id}
      className={cn(
        "font-mono text-c3 text-[10px] tracking-[0.2em] uppercase",
        className,
      )}
    >
      {children}
    </p>
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
