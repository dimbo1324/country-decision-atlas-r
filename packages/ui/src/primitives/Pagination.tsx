"use client";

import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "../lib/cn";

interface PaginationProps {
  page: number;
  pageCount: number;
  onPageChange: (page: number) => void;
  className?: string;
  /** This package has no i18n context of its own (Storybook renders it
   * with none at all) — callers with a real locale pass translated
   * strings; untranslated callers keep the original Russian defaults. */
  ariaLabel?: string;
  previousLabel?: string;
  nextLabel?: string;
}

export function Pagination({
  page,
  pageCount,
  onPageChange,
  className,
  ariaLabel = "Пагинация",
  previousLabel = "Предыдущая страница",
  nextLabel = "Следующая страница",
}: PaginationProps) {
  if (pageCount <= 1) return null;

  return (
    <nav
      aria-label={ariaLabel}
      className={cn("flex items-center justify-center gap-4", className)}
    >
      <button
        type="button"
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label={previousLabel}
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
        aria-label={nextLabel}
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
