"use client";

import { Accordion, type AccordionItem } from "@country-decision-atlas/ui";
import type { MethodologySection } from "../../shared/api/methodology";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";

const SECTION_TYPE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    index: "index",
    score: "score",
    metric: "metric",
    trust: "trust",
    risk: "risk",
    source: "sources",
    disclaimer: "disclaimer",
  },
  ru: {
    index: "индекс",
    score: "показатель",
    metric: "метрика",
    trust: "доверие",
    risk: "риск",
    source: "источники",
    disclaimer: "дисклеймер",
  },
  es: {
    index: "índice",
    score: "puntuación",
    metric: "métrica",
    trust: "confianza",
    risk: "riesgo",
    source: "fuentes",
    disclaimer: "descargo",
  },
};

export function MethodologyAccordion({
  sections,
}: {
  sections: MethodologySection[];
}) {
  const locale = useAppLocale();
  const items: AccordionItem[] = sections.map((section) => ({
    title: section.title,
    meta:
      SECTION_TYPE_LABELS[locale][section.section_type] ?? section.section_type,
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
