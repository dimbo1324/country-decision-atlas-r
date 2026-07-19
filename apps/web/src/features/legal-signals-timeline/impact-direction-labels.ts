import type { SupportedLocale } from "../../shared/lib/locale";

export const IMPACT_DIRECTION_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    positive: "Positive",
    negative: "Negative",
    neutral: "Neutral",
    mixed: "Mixed",
    uncertain: "Uncertain",
  },
  ru: {
    positive: "Положительное",
    negative: "Негативное",
    neutral: "Нейтральное",
    mixed: "Смешанное",
    uncertain: "Неопределённое",
  },
  es: {
    positive: "Positivo",
    negative: "Negativo",
    neutral: "Neutral",
    mixed: "Mixto",
    uncertain: "Incierto",
  },
};

export function impactDirectionLabel(
  locale: SupportedLocale,
  value: string,
): string {
  return IMPACT_DIRECTION_LABELS[locale][value] ?? value;
}
