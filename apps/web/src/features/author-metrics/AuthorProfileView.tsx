"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3 } from "lucide-react";
import {
  Badge,
  Kicker,
  MetricCard,
  ProgressRing,
} from "@country-decision-atlas/ui";
import {
  authorPublicMetricsQuery,
  authorReputationQuery,
} from "../../entities/author-metrics/api";
import { isApiError } from "../../shared/api/http";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LoadingState } from "../../shared/ui/LoadingState";

export function AuthorProfileView({ userId }: { userId: string }) {
  const reputation = useQuery(authorReputationQuery(userId));
  const metrics = useQuery(authorPublicMetricsQuery(userId));

  if (reputation.isPending || metrics.isPending) {
    return <LoadingState message="Загрузка профиля автора…" />;
  }

  // Reputation is computed periodically, not on first request -- a fresh or
  // low-activity author legitimately has no AuthorReputationResponse yet
  // (backend returns author_reputation_not_found). That's a real, expected
  // state, not a page-level failure: still show the author's metrics.
  const reputationNotComputed =
    reputation.isError &&
    isApiError(reputation.error) &&
    reputation.error.error?.code === "author_reputation_not_found";

  if (reputation.isError && !reputationNotComputed) {
    return (
      <ErrorState
        error={isApiError(reputation.error) ? reputation.error : undefined}
      />
    );
  }

  const rep = reputation.data;
  const overallScore = rep
    ? Math.round(
        (rep.coverage_score + rep.freshness_score + rep.sourcing_score) / 3,
      )
    : 0;
  const metricItems = metrics.data?.items ?? [];

  return (
    <div
      className="flex flex-col gap-8"
      data-testid="author-profile-view"
    >
      <div className="flex flex-wrap items-center gap-8">
        <ProgressRing
          value={overallScore}
          label="Репутация"
          active={Boolean(rep)}
        />
        {rep ? (
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">Подписчики: {rep.subscriber_count}</Badge>
            <Badge variant="default">
              Опубликовано метрик: {rep.published_metric_count}
            </Badge>
            <Badge variant="default">
              Покрытие: {Math.round(rep.coverage_score)}
            </Badge>
            <Badge variant="default">
              Свежесть: {Math.round(rep.freshness_score)}
            </Badge>
            <Badge variant="default">
              Источники: {Math.round(rep.sourcing_score)}
            </Badge>
          </div>
        ) : (
          <p
            className="text-c3 text-sm"
            data-testid="author-reputation-not-computed"
          >
            Репутация ещё не рассчитана.
          </p>
        )}
      </div>

      <div className="flex flex-col gap-4">
        <Kicker>Метрики автора</Kicker>
        {metricItems.length === 0 ? (
          <div data-testid="author-profile-metrics-empty-state">
            <EmptyState message="У автора пока нет опубликованных метрик." />
          </div>
        ) : (
          <div
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
            data-testid="author-profile-metrics-list"
          >
            {metricItems.map((metric) => (
              <MetricCard
                key={metric.id}
                icon={BarChart3}
                name={metric.name_ru}
                tag={metric.slug}
                description={metric.methodology_ru || metric.methodology_en}
                value={`${metric.scale_min}–${metric.scale_max}`}
                unit={
                  metric.polarity === "higher_is_better"
                    ? "выше — лучше"
                    : "ниже — лучше"
                }
                accent="gold"
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
