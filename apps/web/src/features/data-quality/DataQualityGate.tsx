"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  dataQualityApi,
  type DataQualityReport,
} from "../../shared/api/data-quality";
import { isApiError } from "../../shared/api/http";
import { useAuth } from "../../shared/auth/AuthProvider";
import { routes } from "../../shared/lib/routes";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";
import { DataQualityReportView } from "./DataQualityReportView";

const ALLOWED_ROLES = new Set(["editor", "admin", "owner"]);

export function DataQualityGate() {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [report, setReport] = useState<DataQualityReport | null>(null);
  const [error, setError] = useState<unknown | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAllowed = user !== null && ALLOWED_ROLES.has(user.role);

  useEffect(() => {
    if (isAuthLoading || !isAllowed) {
      setIsLoading(false);
      return;
    }
    let active = true;
    setIsLoading(true);
    dataQualityApi
      .getDataQualityReport()
      .then((response) => {
        if (active) setReport(response);
      })
      .catch((err: unknown) => {
        if (active) setError(err);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });
    return () => {
      active = false;
    };
  }, [isAuthLoading, isAllowed]);

  if (isAuthLoading) {
    return <LoadingState message="Загрузка…" />;
  }

  if (!user) {
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

  if (!isAllowed) {
    return (
      <div
        className="notice"
        data-testid="data-quality-forbidden"
      >
        У вашей роли нет доступа к отчёту качества данных.
      </div>
    );
  }

  if (isLoading) {
    return <LoadingState message="Загрузка отчёта качества данных…" />;
  }

  if (error) {
    return (
      <div data-testid="data-quality-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return <DataQualityReportView report={report} />;
}
