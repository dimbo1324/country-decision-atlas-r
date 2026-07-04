import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet, queryString } from "./http";

export type FeatureAccessTier = components["schemas"]["FeatureAccessTier"];
export type FeatureFlag = components["schemas"]["FeatureFlag"];
export type FeatureFlagListResponse =
  components["schemas"]["FeatureFlagListResponse"];
export type FeatureFlagDetailResponse =
  components["schemas"]["FeatureFlagDetailResponse"];

export function getFeatures(
  accessTier: FeatureAccessTier = "public",
): Promise<FeatureFlagListResponse> {
  return apiGet<FeatureFlagListResponse>(
    `/api/v1/platform/features${queryString({ access_tier: accessTier })}`,
  );
}

export function getFeature(
  featureKey: string,
  accessTier: FeatureAccessTier = "public",
): Promise<FeatureFlagDetailResponse> {
  return apiGet<FeatureFlagDetailResponse>(
    `/api/v1/platform/features/${featureKey}${queryString({
      access_tier: accessTier,
    })}`,
  );
}

export const featureFlagsApi = {
  getFeatures,
  getFeature,
};
