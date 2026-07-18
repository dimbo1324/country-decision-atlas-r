import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

type Confidence = "low" | "medium" | "high" | string;

type ConfidenceBadgeProps = {
  confidence: Confidence;
};

const CONFIDENCE_VARIANT: Record<string, BadgeVariant> = {
  high: "trust",
  medium: "info",
  low: "warning",
};

const CONFIDENCE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    high: "high",
    medium: "medium",
    low: "low",
  },
  ru: {
    high: "высокая",
    medium: "средняя",
    low: "низкая",
  },
  es: {
    high: "alta",
    medium: "media",
    low: "baja",
  },
};

const CONFIDENCE_PREFIX: Record<SupportedLocale, string> = {
  en: "Confidence",
  ru: "Достоверность",
  es: "Certeza",
};

/** Lowercase confidence level in the given interface locale, for reuse
 * outside the badge. */
export function confidenceLabel(
  confidence: string,
  locale: SupportedLocale,
): string {
  return CONFIDENCE_LABELS[locale][confidence] ?? confidence;
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
  const locale = useAppLocale();
  const variant = CONFIDENCE_VARIANT[confidence] ?? "default";
  const label = confidenceLabel(confidence, locale);
  return (
    <Badge variant={variant}>
      {CONFIDENCE_PREFIX[locale]}: {label}
    </Badge>
  );
}
