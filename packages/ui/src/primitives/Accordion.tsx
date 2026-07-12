"use client";

import { useId, useState, type ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "../lib/cn";

export interface AccordionItem {
  title: string;
  meta?: string;
  content: ReactNode;
}

interface AccordionProps {
  items: AccordionItem[];
  className?: string;
}

export function Accordion({ items, className }: AccordionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  const baseId = useId();

  return (
    <div className={cn("border-warm flex flex-col border-t", className)}>
      {items.map((item, index) => {
        const open = openIndex === index;
        const panelId = `${baseId}-panel-${index}`;
        return (
          <div
            key={item.title}
            className="border-warm border-b"
          >
            <button
              type="button"
              aria-expanded={open}
              aria-controls={panelId}
              onClick={() => setOpenIndex(open ? null : index)}
              className="group flex w-full items-center justify-between gap-4 py-3.5 text-left"
            >
              <span
                className={cn(
                  "font-body text-sm transition-colors duration-300",
                  open ? "text-c1" : "text-c2 group-hover:text-c1",
                )}
              >
                {item.title}
              </span>
              <span className="flex shrink-0 items-center gap-3">
                {item.meta && (
                  <span className="font-mono text-c4 text-[8px] tracking-[0.18em] uppercase">
                    {item.meta}
                  </span>
                )}
                <ChevronDown
                  width={14}
                  height={14}
                  strokeWidth={1.5}
                  className={cn(
                    "text-c3 transition-transform duration-500",
                    open && "text-c1 rotate-180",
                  )}
                  style={{ transitionTimingFunction: "var(--ease-arrive)" }}
                />
              </span>
            </button>
            {/* Grid-rows trick animates open/close to the content's natural
                height — no max-height magic number to outgrow. */}
            <div
              id={panelId}
              className="grid transition-[grid-template-rows] duration-500"
              style={{
                gridTemplateRows: open ? "1fr" : "0fr",
                transitionTimingFunction: "var(--ease-arrive)",
              }}
            >
              <div className="overflow-hidden">
                <div className="text-c3 pb-4 text-sm leading-relaxed">
                  {item.content}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
