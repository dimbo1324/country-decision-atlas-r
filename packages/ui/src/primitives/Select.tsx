"use client";

import type { ComponentPropsWithoutRef, ElementRef } from "react";
import { forwardRef } from "react";
import { Check, ChevronDown, ChevronUp } from "lucide-react";
import * as SelectPrimitive from "@radix-ui/react-select";
import { cn } from "../lib/cn";

export const Select = SelectPrimitive.Root;
export const SelectGroup = SelectPrimitive.Group;
export const SelectValue = SelectPrimitive.Value;

export const SelectTrigger = forwardRef<
  ElementRef<typeof SelectPrimitive.Trigger>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Trigger>
>(({ className, children, ...rest }, ref) => (
  <SelectPrimitive.Trigger
    ref={ref}
    className={cn(
      "border-warm bg-bg2 text-c1 font-body flex w-full items-center justify-between gap-2 border px-4 py-2.5 text-sm transition-colors duration-300 hover:border-[var(--color-c3)] focus:outline-none data-[placeholder]:text-c3",
      className,
    )}
    {...rest}
  >
    {children}
    <SelectPrimitive.Icon asChild>
      <ChevronDown
        width={14}
        height={14}
        strokeWidth={1.5}
        className="text-c3 shrink-0"
      />
    </SelectPrimitive.Icon>
  </SelectPrimitive.Trigger>
));
SelectTrigger.displayName = "SelectTrigger";

export const SelectContent = forwardRef<
  ElementRef<typeof SelectPrimitive.Content>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Content>
>(({ className, children, ...rest }, ref) => (
  <SelectPrimitive.Portal>
    <SelectPrimitive.Content
      ref={ref}
      className={cn(
        "bg-bg3 border-warm z-[85] overflow-hidden border shadow-[0_12px_32px_rgb(0_0_0/0.4)]",
        className,
      )}
      position="popper"
      sideOffset={6}
      {...rest}
    >
      <SelectPrimitive.ScrollUpButton className="text-c3 flex items-center justify-center py-1">
        <ChevronUp
          width={13}
          height={13}
        />
      </SelectPrimitive.ScrollUpButton>
      <SelectPrimitive.Viewport className="p-1">{children}</SelectPrimitive.Viewport>
      <SelectPrimitive.ScrollDownButton className="text-c3 flex items-center justify-center py-1">
        <ChevronDown
          width={13}
          height={13}
        />
      </SelectPrimitive.ScrollDownButton>
    </SelectPrimitive.Content>
  </SelectPrimitive.Portal>
));
SelectContent.displayName = "SelectContent";

export const SelectItem = forwardRef<
  ElementRef<typeof SelectPrimitive.Item>,
  ComponentPropsWithoutRef<typeof SelectPrimitive.Item>
>(({ className, children, ...rest }, ref) => (
  <SelectPrimitive.Item
    ref={ref}
    className={cn(
      "text-c2 data-[highlighted]:bg-bg4 data-[highlighted]:text-c1 relative flex cursor-pointer items-center justify-between gap-3 px-3 py-2 text-sm outline-none transition-colors duration-150",
      className,
    )}
    {...rest}
  >
    <SelectPrimitive.ItemText>{children}</SelectPrimitive.ItemText>
    <SelectPrimitive.ItemIndicator>
      <Check
        width={13}
        height={13}
        strokeWidth={1.5}
        className="text-gold3"
      />
    </SelectPrimitive.ItemIndicator>
  </SelectPrimitive.Item>
));
SelectItem.displayName = "SelectItem";
