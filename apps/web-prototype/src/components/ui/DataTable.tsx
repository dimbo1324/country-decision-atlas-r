import type { ReactNode } from "react";
import { cn } from "@/lib/cn";

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
 * a left-origin sweep and its text brightens. */
export function DataTable({ columns, rows, className }: DataTableProps) {
  return (
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
                    // The sweep underline lives on the first cell so it can
                    // span the row via absolute positioning.
                    cellIndex === 0 && "relative",
                  )}
                >
                  {cell}
                  {cellIndex === 0 && (
                    <span className="bg-gold2/70 pointer-events-none absolute bottom-0 left-0 h-px w-[100vw] max-w-none origin-left scale-x-0 transition-transform duration-500 group-hover:scale-x-100" />
                  )}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
