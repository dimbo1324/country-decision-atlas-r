import type { components } from "@country-decision-atlas/contracts/generated/types";

// Fetching now goes through entities/search/api.ts's searchQuery
// (TanStack Query + openapi-fetch) — these type aliases are the only
// reason this module still exists.
export type SearchResultItem = components["schemas"]["SearchResultItem"];
export type SearchResponse = components["schemas"]["SearchResponse"];
