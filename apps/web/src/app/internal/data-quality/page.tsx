import { dataQualityApi } from "../../../shared/api";
import { DataQualityReportView } from "../../../features/data-quality";
import { ErrorState } from "../../../shared/ui/ErrorState";

export const dynamic = "force-dynamic";

export default async function DataQualityPage() {
  const adminToken = process.env.ADMIN_TOKEN;

  if (!adminToken) {
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Internal</p>
          <h1>Data quality report</h1>
        </header>
        <ErrorState error="ADMIN_TOKEN is not configured on this server." />
      </div>
    );
  }

  let report;
  try {
    report = await dataQualityApi.getDataQualityReport(adminToken);
  } catch (err: unknown) {
    const message =
      err instanceof Error ? err.message : "Failed to load data quality report.";
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Internal</p>
          <h1>Data quality report</h1>
        </header>
        <ErrorState error={message} />
      </div>
    );
  }

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Internal</p>
        <h1>Data quality report</h1>
      </header>
      <DataQualityReportView report={report} />
    </div>
  );
}
