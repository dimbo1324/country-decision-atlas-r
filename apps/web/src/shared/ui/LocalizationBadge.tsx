import type { components } from "@country-decision-atlas/contracts/generated/types";
import {
  getLocalizationBadgeLabel,
  getLocalizationBadgeTitle,
  getLocalizationBadgeVariant,
} from "../lib/localization-labels";

type LocalizationMeta = components["schemas"]["LocalizationMeta"];

type LocalizationBadgeProps = {
  localization?: LocalizationMeta | null;
  compact?: boolean;
};

export function LocalizationBadge({
  localization,
  compact = false,
}: LocalizationBadgeProps) {
  if (!localization) return null;
  const label = getLocalizationBadgeLabel(localization);
  if (!label) return null;
  const title = getLocalizationBadgeTitle(localization);
  const variant = getLocalizationBadgeVariant(localization);
  const className = [
    "localizationBadge",
    compact ? "localizationBadgeCompact" : "",
    variant,
  ]
    .filter(Boolean)
    .join(" ");
  return (
    <span
      className={className}
      title={title ?? undefined}
      data-testid="localization-badge"
    >
      {label}
    </span>
  );
}
