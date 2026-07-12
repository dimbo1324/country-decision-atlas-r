"use client";

import type { ComponentPropsWithoutRef, ElementRef, ReactNode } from "react";
import { forwardRef } from "react";
import { X } from "lucide-react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { cn } from "../lib/cn";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export const DialogContent = forwardRef<
  ElementRef<typeof DialogPrimitive.Content>,
  ComponentPropsWithoutRef<typeof DialogPrimitive.Content> & {
    title: ReactNode;
    description?: ReactNode;
  }
>(({ className, children, title, description, ...rest }, ref) => (
  <DialogPrimitive.Portal>
    <DialogPrimitive.Overlay className="fixed inset-0 z-[90] bg-black/60 backdrop-blur-[3px]" />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "bg-bg4 border-warm fixed top-1/2 left-1/2 z-[91] w-full max-w-md -translate-x-1/2 -translate-y-1/2 border p-7 focus:outline-none",
        className,
      )}
      {...rest}
    >
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <DialogPrimitive.Title className="font-display text-c1 text-xl font-semibold">
            {title}
          </DialogPrimitive.Title>
          {description && (
            <DialogPrimitive.Description className="text-c3 mt-1.5 text-sm leading-relaxed">
              {description}
            </DialogPrimitive.Description>
          )}
        </div>
        <DialogPrimitive.Close
          aria-label="Закрыть"
          className="border-warm text-c2 hover:border-warm-hi hover:text-c1 flex h-8 w-8 shrink-0 items-center justify-center border transition-colors duration-300"
        >
          <X
            width={14}
            height={14}
            strokeWidth={1.5}
          />
        </DialogPrimitive.Close>
      </div>
      {children}
    </DialogPrimitive.Content>
  </DialogPrimitive.Portal>
));
DialogContent.displayName = "DialogContent";
