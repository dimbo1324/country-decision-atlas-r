import { Badge, type BadgeVariant } from "@country-decision-atlas/ui";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

type FreshnessStatus = "fresh" | "aging" | "stale" | "unknown" | string;

type FreshnessBadgeProps = {
  status: FreshnessStatus;
};

const FRESHNESS_VARIANT: Record<string, BadgeVariant> = {
  fresh: "trust",
  aging: "info",
  stale: "warning",
  unknown: "default",
};

const FRESHNESS_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    fresh: "fresh",
    aging: "aging",
    stale: "stale",
    unknown: "unknown",
  },
  ru: {
    fresh: "актуальные",
    aging: "устаревающие",
    stale: "устаревшие",
    unknown: "неизвестно",
  },
  es: {
    fresh: "actualizados",
    aging: "envejeciendo",
    stale: "desactualizados",
    unknown: "desconocido",
  },
};

const FRESHNESS_PREFIX: Record<SupportedLocale, string> = {
  en: "Data",
  ru: "Данные",
  es: "Datos",
};

export function FreshnessBadge({ status }: FreshnessBadgeProps) {
  const locale = useAppLocale();
  const variant = FRESHNESS_VARIANT[status] ?? "default";
  const label = FRESHNESS_LABELS[locale][status] ?? status;
  return (
    <Badge variant={variant}>
      {FRESHNESS_PREFIX[locale]}: {label}
    </Badge>
  );
}
