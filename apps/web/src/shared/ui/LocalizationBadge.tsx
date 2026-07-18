import { Badge, type BadgeVariant, cn } from "@country-decision-atlas/ui";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import {
  getLocalizationBadgeLabel,
  getLocalizationBadgeTitle,
  getLocalizationBadgeVariant,
} from "../lib/localization-labels";
import { useAppLocale } from "../lib/useAppLocale";

type LocalizationMeta = components["schemas"]["LocalizationMeta"];

type LocalizationBadgeProps = {
  localization?: LocalizationMeta | null;
  compact?: boolean;
};

const VARIANT_MAP: Record<string, BadgeVariant> = {
  localizationBadgeStale: "warning",
  localizationBadgeMissing: "default",
  localizationBadgeFallback: "info",
  localizationBadgeMachine: "info",
  localizationBadgeReviewed: "trust",
  localizationBadgeOriginal: "positive",
  localizationBadgeNeedsReview: "warning",
};

export function LocalizationBadge({
  localization,
  compact = false,
}: LocalizationBadgeProps) {
  const locale = useAppLocale();
  if (!localization) return null;
  const label = getLocalizationBadgeLabel(localization, locale);
  if (!label) return null;
  const title = getLocalizationBadgeTitle(localization, locale);
  const variant =
    VARIANT_MAP[getLocalizationBadgeVariant(localization)] ?? "default";
  return (
    <Badge
      variant={variant}
      title={title ?? undefined}
    >
      <span
        data-testid="localization-badge"
        className={cn(compact && "text-[8px]")}
      >
        {label}
      </span>
    </Badge>
  );
}
