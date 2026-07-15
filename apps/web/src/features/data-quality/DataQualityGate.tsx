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
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="data-quality-unauthenticated"
      >
        <p className="text-c3 text-sm">
          Войдите с ролью editor/admin/owner, чтобы посмотреть отчёт качества
          данных.{" "}
          <Link
            href={routes.login}
            className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
          >
            Войти
          </Link>
        </p>
      </div>
    );
  }

  if (status === "forbidden") {
    return (
      <div
        className="border-warm flex flex-col gap-2 border px-4 py-4"
        data-testid="data-quality-forbidden"
      >
        <p className="text-c3 text-sm">
          У вашей роли нет доступа к отчёту качества данных.
        </p>
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
