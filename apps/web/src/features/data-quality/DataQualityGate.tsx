"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { dataQualityApi } from "../../shared/api/data-quality";
import { isApiError } from "../../shared/api/http";
import { DATA_QUALITY_ROLES } from "../../shared/auth/roles";
import { useAuthGuard } from "../../shared/auth/useAuthGuard";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { DataQualityReportView } from "./DataQualityReportView";

export function DataQualityGate() {
  const { status } = useAuthGuard(DATA_QUALITY_ROLES);
  const report = useQuery({
    queryKey: ["admin", "data-quality", "report"] as const,
    queryFn: () => dataQualityApi.getDataQualityReport(),
    enabled: status === "ok",
  });

  if (status === "loading") {
    return <LoadingState message="Загрузка…" />;
  }

  if (status === "unauthenticated") {
    return (
      <div
        className="notice"
        data-testid="data-quality-unauthenticated"
      >
        Войдите с ролью editor/admin/owner, чтобы посмотреть отчёт качества
        данных. <Link href={routes.login}>Войти</Link>
      </div>
    );
  }

  if (status === "forbidden") {
    return (
      <div
        className="notice"
        data-testid="data-quality-forbidden"
      >
        У вашей роли нет доступа к отчёту качества данных.
      </div>
    );
  }

  if (report.isPending) {
    return <LoadingState message="Загрузка отчёта качества данных…" />;
  }

  if (report.isError || !report.data) {
    return (
      <div data-testid="data-quality-error">
        <ErrorState
          error={isApiError(report.error) ? report.error : undefined}
        />
      </div>
    );
  }

  return <DataQualityReportView report={report.data} />;
}
