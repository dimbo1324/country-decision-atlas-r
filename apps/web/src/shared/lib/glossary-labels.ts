import type { SupportedLocale } from "./locale";

export const GLOSSARY_CATEGORY_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    migration: "migration",
    legal: "legal",
    analytics: "analytics",
    trust: "trust",
    source: "sources",
    decision: "decisions",
    route: "routes",
    persona: "personas",
  },
  ru: {
    migration: "миграция",
    legal: "право",
    analytics: "аналитика",
    trust: "доверие",
    source: "источники",
    decision: "решения",
    route: "маршруты",
    persona: "персоны",
  },
  es: {
    migration: "migración",
    legal: "legal",
    analytics: "analítica",
    trust: "confianza",
    source: "fuentes",
    decision: "decisiones",
    route: "rutas",
    persona: "personas",
  },
};

export const GLOSSARY_CATEGORIES: string[] = Object.keys(
  GLOSSARY_CATEGORY_LABELS.en,
);

export function glossaryCategoryLabel(
  category: string,
  locale: SupportedLocale,
): string {
  return GLOSSARY_CATEGORY_LABELS[locale][category] ?? category;
}
