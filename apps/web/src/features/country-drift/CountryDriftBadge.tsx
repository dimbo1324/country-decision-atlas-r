import { useTranslations } from "next-intl";
import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";

type DriftLabel =
  | "insufficient_data"
  | "negative"
  | "stable"
  | "mildly_positive"
  | "positive"
  | string;

type CountryDriftBadgeProps = {
  label: DriftLabel;
};

const DRIFT_VARIANT: Record<string, BadgeVariant> = {
  positive: "trust",
  mildly_positive: "info",
  stable: "default",
  negative: "warning",
  insufficient_data: "default",
};

const DRIFT_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    positive: "Direction: improving",
    mildly_positive: "Direction: mildly improving",
    stable: "Direction: stable",
    negative: "Direction: worsening",
    insufficient_data: "Not enough data",
  },
  ru: {
    positive: "Направление: улучшается",
    mildly_positive: "Направление: умеренно улучшается",
    stable: "Направление: стабильно",
    negative: "Направление: ухудшается",
    insufficient_data: "Недостаточно данных",
  },
  es: {
    positive: "Dirección: mejorando",
    mildly_positive: "Dirección: mejorando levemente",
    stable: "Dirección: estable",
    negative: "Dirección: empeorando",
    insufficient_data: "Datos insuficientes",
  },
};

export function CountryDriftBadge({ label }: CountryDriftBadgeProps) {
  const t = useTranslations("countryDrift");
  const locale = useAppLocale();
  return (
    <Badge
      variant={DRIFT_VARIANT[label] ?? "default"}
      title={t("badgeTitle")}
    >
      {DRIFT_LABELS[locale][label] ?? label}
    </Badge>
  );
}
