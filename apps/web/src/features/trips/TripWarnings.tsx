"use client";

import { useQuery } from "@tanstack/react-query";
import { Badge } from "@country-decision-atlas/ui";
import {
  tripWarningsQuery,
  tripWhatChangedQuery,
} from "../../entities/trips/api";
import { isApiError } from "../../shared/api/http";
import { LoadingState } from "../../shared/ui/LoadingState";

const SEVERITY_LABELS: Record<string, string> = {
  low: "Низкий",
  medium: "Средний",
  high: "Высокий",
  critical: "Критический",
};

export function TripWarnings({ tripId }: { tripId: string }) {
  const warnings = useQuery(tripWarningsQuery(tripId));
  const whatChanged = useQuery(tripWhatChangedQuery(tripId));

  if (warnings.isPending) {
    return <LoadingState message="Загрузка предупреждений…" />;
  }

  if (warnings.isError) {
    return (
      <p
        className="text-c4 text-sm"
        data-testid="trip-warnings-error"
      >
        {isApiError(warnings.error)
          ? (warnings.error.error?.message ??
            "Не удалось загрузить предупреждения.")
          : "Не удалось загрузить предупреждения."}
      </p>
    );
  }

  const items = warnings.data.items ?? [];
  const whatChangedCountries = whatChanged.data?.countries ?? [];

  return (
    <div
      className="flex flex-col gap-4"
      data-testid="trip-warnings"
    >
      {items.length === 0 ? (
        <p className="text-c3 text-sm">Предупреждений нет.</p>
      ) : (
        <div className="flex flex-col gap-2">
          {items.map((warning, index) => (
            <div
              key={`${warning.code}-${index}`}
              className="border-terra2/60 flex flex-col gap-1 border px-4 py-3"
              data-testid="trip-warning-item"
            >
              <div className="flex items-center gap-2">
                <Badge variant="default">
                  {SEVERITY_LABELS[warning.severity] ?? warning.severity}
                </Badge>
              </div>
              <p className="text-terra3 text-sm">{warning.message}</p>
            </div>
          ))}
        </div>
      )}

      {whatChangedCountries.length > 0 && (
        <div
          className="flex flex-wrap gap-2"
          data-testid="trip-what-changed"
        >
          {whatChangedCountries.map((c) => (
            <Badge
              key={c.country_slug}
              variant="default"
            >
              {c.country_slug}: {c.total} изменений
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
