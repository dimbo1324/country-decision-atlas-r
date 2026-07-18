import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

type TrustLabel =
  | "very_high"
  | "high"
  | "medium"
  | "low"
  | "very_low"
  | "insufficient_data"
  | string;

type TrustBadgeProps = {
  label: TrustLabel;
  score?: number | null;
};

const TRUST_VARIANT: Record<string, BadgeVariant> = {
  very_high: "trust",
  high: "trust",
  medium: "info",
  low: "warning",
  very_low: "warning",
  insufficient_data: "default",
};

const TRUST_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    very_high: "Very high",
    high: "High",
    medium: "Medium",
    low: "Low",
    very_low: "Very low",
    insufficient_data: "Insufficient data",
  },
  ru: {
    very_high: "Очень высокое",
    high: "Высокое",
    medium: "Среднее",
    low: "Низкое",
    very_low: "Очень низкое",
    insufficient_data: "Недостаточно данных",
  },
  es: {
    very_high: "Muy alta",
    high: "Alta",
    medium: "Media",
    low: "Baja",
    very_low: "Muy baja",
    insufficient_data: "Datos insuficientes",
  },
};

const TRUST_PREFIX: Record<SupportedLocale, string> = {
  en: "Trust",
  ru: "Доверие",
  es: "Confianza",
};

const TRUST_TITLE: Record<SupportedLocale, string> = {
  en: "Data-quality indicator",
  ru: "Индикатор качества данных",
  es: "Indicador de calidad de datos",
};

/** Trust level label in the given interface locale, for reuse outside the
 * badge (e.g. a `ProgressRing` label). */
export function trustLabel(label: string, locale: SupportedLocale): string {
  return TRUST_LABELS[locale][label] ?? label;
}

export function TrustBadge({ label, score }: TrustBadgeProps) {
  const locale = useAppLocale();
  const variant = TRUST_VARIANT[label] ?? "default";
  const text = trustLabel(label, locale);
  return (
    <Badge
      variant={variant}
      title={TRUST_TITLE[locale]}
    >
      {TRUST_PREFIX[locale]}: {text}
      {score != null && ` (${score.toFixed(0)})`}
    </Badge>
  );
}
