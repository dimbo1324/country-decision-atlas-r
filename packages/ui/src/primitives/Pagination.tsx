"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "../lib/cn";

interface PaginationProps {
  page: number;
  pageCount: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export function Pagination({
  page,
  pageCount,
  onPageChange,
  className,
}: PaginationProps) {
  if (pageCount <= 1) return null;

  return (
    <nav
      aria-label="Пагинация"
      className={cn("flex items-center justify-center gap-4", className)}
    >
      <button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Предыдущая страница"
        className="border-warm text-c2 hover:border-warm-hi hover:text-c1 flex h-8 w-8 items-center justify-center border transition-colors duration-300 disabled:pointer-events-none disabled:opacity-30"
      >
        <ChevronLeft
          width={14}
          height={14}
          strokeWidth={1.5}
        />
      </button>
      <span className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
        {page} / {pageCount}
      </span>
      <button
        type="button"
        onClick={() => onPageChange(page + 1)}
        disabled={page >= pageCount}
        aria-label="Следующая страница"
        className="border-warm text-c2 hover:border-warm-hi hover:text-c1 flex h-8 w-8 items-center justify-center border transition-colors duration-300 disabled:pointer-events-none disabled:opacity-30"
      >
        <ChevronRight
          width={14}
          height={14}
          strokeWidth={1.5}
        />
      </button>
    </nav>
  );
}
