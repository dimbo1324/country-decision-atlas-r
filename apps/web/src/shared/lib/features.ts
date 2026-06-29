import type { FeatureFlag, FeatureFlagListResponse } from "../api/feature-flags";

export function isFeatureEnabled(
  features: FeatureFlagListResponse | FeatureFlag[] | null | undefined,
  featureKey: string,
): boolean {
  const items = Array.isArray(features) ? features : features?.items;
  const feature = items?.find((item) => item.key === featureKey);
  return Boolean(feature?.is_enabled_for_context);
}
