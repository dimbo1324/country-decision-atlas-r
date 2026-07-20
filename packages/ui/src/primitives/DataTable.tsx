"use client";

import type { ReactNode } from "react";
import { cn } from "../lib/cn";

export interface DataTableColumn {
  header: string;
  align?: "left" | "right";
  /** Numeric columns render in the mono face per the design system. */
  numeric?: boolean;
}

interface DataTableProps {
  columns: DataTableColumn[];
  rows: ReactNode[][];
  className?: string;
}

/** Design-system table: horizontal borders only, hover row underlines with
 * a left-origin sweep and its text brightens. Wrapped in an `overflow-x-auto`
 * scroll container so a wide table (e.g. the 5-column dossier score
 * breakdown) scrolls horizontally on narrow viewports instead of being
 * clipped by an ancestor `overflow-hidden` card — otherwise the rightmost
 * columns are unreachable on mobile. */
export function DataTable({ columns, rows, className }: DataTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={cn("w-full border-collapse", className)}>
        <thead>
          <tr className="border-warm border-b">
            {columns.map((column) => (
              <th
                key={column.header}
                className={cn(
                  "font-mono text-c4 px-3 py-2.5 text-[8px] font-normal tracking-[0.2em] uppercase",
                  column.align === "right" ? "text-right" : "text-left",
                )}
              >
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="group border-warm relative border-b"
            >
              {row.map((cell, cellIndex) => {
                const column = columns[cellIndex];
                return (
                  <td
                    key={cellIndex}
                    className={cn(
                      "text-c2 group-hover:text-c1 px-3 py-3 text-sm transition-colors duration-300",
                      column?.numeric && "font-mono text-[11px]",
                      column?.align === "right" ? "text-right" : "text-left",
                    )}
                  >
                    {cell}
                    {cellIndex === 0 && (
                      // Sweep underline spans the whole row: the `<tr>` is the
                      // relative containing block, so `left-0 right-0` sizes to
                      // the row exactly. (Previously `w-[100vw]` overshot the
                      // viewport, which would force a permanent horizontal
                      // scrollbar now that the table sits in `overflow-x-auto`.)
                      <span className="bg-gold2/70 pointer-events-none absolute right-0 bottom-0 left-0 h-px origin-left scale-x-0 transition-transform duration-500 group-hover:scale-x-100" />
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
