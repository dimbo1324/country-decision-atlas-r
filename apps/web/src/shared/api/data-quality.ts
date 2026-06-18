import type { components } from "@country-decision-atlas/contracts/generated/types";

import { apiGet } from "./http";

export type DataQualityReport = components["schemas"]["DataQualityReport"];

export function getDataQualityReport(adminToken: string): Promise<DataQualityReport> {
  return apiGet<DataQualityReport>("/api/v1/admin/data-quality/report", {
    headers: {
      "X-Admin-Token": adminToken,
    },
  });
}

export const dataQualityApi = {
  getDataQualityReport,
};
