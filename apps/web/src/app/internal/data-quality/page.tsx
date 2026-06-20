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
          <p className="eyebrow">Внутреннее</p>
          <h1>Отчёт качества данных</h1>
        </header>
        <ErrorState error="ADMIN_TOKEN не настроен на сервере." />
      </div>
    );
  }

  let report;
  try {
    report = await dataQualityApi.getDataQualityReport(adminToken);
  } catch (err: unknown) {
    const message =
      err instanceof Error
        ? err.message
        : "Не удалось загрузить отчёт качества данных.";
    return (
      <div className="pageShell">
        <header className="pageHeader">
          <p className="eyebrow">Внутреннее</p>
          <h1>Отчёт качества данных</h1>
        </header>
        <ErrorState error={message} />
      </div>
    );
  }

  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Внутреннее</p>
        <h1>Отчёт качества данных</h1>
      </header>
      <DataQualityReportView report={report} />
    </div>
  );
}
