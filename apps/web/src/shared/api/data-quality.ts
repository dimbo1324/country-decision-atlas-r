import type { components } from "@country-decision-atlas/contracts/generated/types";

import { authHeaders } from "../auth/session";
import { apiGet } from "./http";

export type DataQualityReport = components["schemas"]["DataQualityReport"];

export function getDataQualityReport(): Promise<DataQualityReport> {
  return apiGet<DataQualityReport>("/api/v1/admin/data-quality/report", {
    headers: authHeaders(),
  });
}

export const dataQualityApi = {
  getDataQualityReport,
};
