"use client";

import type { ComponentPropsWithoutRef, ElementRef } from "react";
import { forwardRef } from "react";
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu";
import { cn } from "../lib/cn";

export const DropdownMenu = DropdownMenuPrimitive.Root;
export const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger;
export const DropdownMenuGroup = DropdownMenuPrimitive.Group;

export const DropdownMenuContent = forwardRef<
  ElementRef<typeof DropdownMenuPrimitive.Content>,
  ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>
>(({ className, sideOffset = 6, ...rest }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "bg-bg3 border-warm z-[85] min-w-[10rem] overflow-hidden border p-1 shadow-[0_12px_32px_rgb(0_0_0/0.4)]",
        className,
      )}
      {...rest}
    />
  </DropdownMenuPrimitive.Portal>
));
DropdownMenuContent.displayName = "DropdownMenuContent";

export const DropdownMenuItem = forwardRef<
  ElementRef<typeof DropdownMenuPrimitive.Item>,
  ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item>
>(({ className, ...rest }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "text-c2 data-[highlighted]:bg-bg4 data-[highlighted]:text-c1 flex cursor-pointer items-center gap-2 px-3 py-2 text-sm outline-none transition-colors duration-150",
      className,
    )}
    {...rest}
  />
));
DropdownMenuItem.displayName = "DropdownMenuItem";

export const DropdownMenuSeparator = forwardRef<
  ElementRef<typeof DropdownMenuPrimitive.Separator>,
  ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>
>(({ className, ...rest }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    className={cn("border-warm my-1 border-t", className)}
    {...rest}
  />
));
DropdownMenuSeparator.displayName = "DropdownMenuSeparator";

export const DropdownMenuLabel = forwardRef<
  ElementRef<typeof DropdownMenuPrimitive.Label>,
  ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label>
>(({ className, ...rest }, ref) => (
  <DropdownMenuPrimitive.Label
    ref={ref}
    className={cn(
      "font-mono text-c4 px-3 py-1.5 text-[9px] tracking-[0.2em] uppercase",
      className,
    )}
    {...rest}
  />
));
DropdownMenuLabel.displayName = "DropdownMenuLabel";
