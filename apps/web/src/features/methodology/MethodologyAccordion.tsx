"use client";

import { Accordion, type AccordionItem } from "@country-decision-atlas/ui";
import type { MethodologySection } from "../../shared/api/methodology";

const SECTION_TYPE_LABELS: Record<string, string> = {
  index: "индекс",
  score: "показатель",
  metric: "метрика",
  trust: "доверие",
  risk: "риск",
  source: "источники",
  disclaimer: "дисклеймер",
};

export function MethodologyAccordion({
  sections,
}: {
  sections: MethodologySection[];
}) {
  const items: AccordionItem[] = sections.map((section) => ({
    title: section.title,
    meta: SECTION_TYPE_LABELS[section.section_type] ?? section.section_type,
    content: (
      <div
        className="flex flex-col gap-3"
        data-testid="methodology-section"
        data-section-type={section.section_type}
      >
        {section.summary && (
          <p className="text-c2 text-sm leading-[1.75]">{section.summary}</p>
        )}
        {section.body &&
          (section.section_type === "disclaimer" ? (
            <blockquote className="font-quote border-gold2/50 text-c2 border-l-2 pl-4 text-base leading-[1.8] italic">
              {section.body}
            </blockquote>
          ) : (
            <p className="text-c3 text-sm leading-[1.75]">{section.body}</p>
          ))}
      </div>
    ),
  }));

  return <Accordion items={items} />;
}
