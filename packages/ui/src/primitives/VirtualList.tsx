"use client";

import { useRef, type ReactNode } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { cn } from "../lib/cn";

interface VirtualListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  /** Row height estimate in px — real rows are measured after mount, this
   * only seeds the initial layout pass. */
  estimateSize?: number;
  /** Registries in this app ship demo-scale item counts, so the container
   * grows to fit its content rather than clipping to a fixed scroll height
   * — every row stays mounted and reachable to tests and screen readers.
   * A generous overscan keeps that true even once real data grows past the
   * synthetic fixtures, until a scroll-clipped variant is actually needed. */
  className?: string;
  overscan?: number;
}

export function VirtualList<T>({
  items,
  renderItem,
  estimateSize = 96,
  className,
  overscan = 20,
}: VirtualListProps<T>) {
  const parentRef = useRef<HTMLDivElement | null>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => estimateSize,
    overscan,
  });

  const virtualItems = virtualizer.getVirtualItems();

  return (
    <div
      ref={parentRef}
      className={cn("relative", className)}
    >
      <div
        style={{
          height: virtualizer.getTotalSize(),
          position: "relative",
          width: "100%",
        }}
      >
        {virtualItems.map((virtualRow) => (
          <div
            key={virtualRow.key}
            data-index={virtualRow.index}
            ref={virtualizer.measureElement}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {renderItem(items[virtualRow.index] as T, virtualRow.index)}
          </div>
        ))}
      </div>
    </div>
  );
}
