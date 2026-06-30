import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

type LocaleCode = components["schemas"]["LocaleCode"];
export type MethodologySection = components["schemas"]["MethodologySection"];
export type MethodologyListResponse = components["schemas"]["MethodologyListResponse"];

export function listMethodologySections(
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<MethodologyListResponse> {
  return apiGet<MethodologyListResponse>(
    `/api/v1/methodology${queryString({ locale })}`,
  );
}

export function getMethodologySection(
  slug: string,
  locale: LocaleCode = DEFAULT_LOCALE,
): Promise<MethodologySection> {
  return apiGet<MethodologySection>(
    `/api/v1/methodology/${slug}${queryString({ locale })}`,
  );
}

export const methodologyApi = { listMethodologySections, getMethodologySection };
