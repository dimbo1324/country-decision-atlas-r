import type { components } from "@country-decision-atlas/contracts/generated/types";

// Fetching now goes through entities/home/api.ts's homeOverviewQuery
// (TanStack Query + openapi-fetch) — these type aliases are the only
// reason this module still exists, kept so the home-overview feature
// components don't need to reach into the generated contract types
// directly.
export type HomeOverviewResponse =
  components["schemas"]["HomeOverviewResponse"];
export type CountryOverviewCard = components["schemas"]["CountryOverviewCard"];
export type ScenarioWinner = components["schemas"]["ScenarioWinner"];
export type HomeMatrixPreview = components["schemas"]["HomeMatrixPreview"];
export type LatestLegalEvent = components["schemas"]["LatestLegalEvent"];
export type HomeKeyInsight = components["schemas"]["HomeKeyInsight"];
