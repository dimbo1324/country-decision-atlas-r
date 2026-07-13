"use client";

import { useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { Badge, ProgressRing, Skeleton } from "@country-decision-atlas/ui";
import { isApiError, type LocaleCode } from "../../shared/api";
import { countryTrustQuery } from "../../entities/trust-surface/api";
import { useNearViewport } from "../../shared/lib/useNearViewport";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../shared/ui/ErrorState";
import { LastVerifiedAt } from "../../shared/ui/LastVerifiedAt";
import { Link } from "../../i18n/navigation";

type TrustSurfaceBlockProps = {
  countrySlug: string;
  locale: LocaleCode;
};

const TRUST_LABEL_ACCENT: Record<string, "sage" | "gold" | "terra"> = {
  high: "sage",
  medium: "gold",
  low: "terra",
};

export function TrustSurfaceBlock({
  countrySlug,
  locale,
}: TrustSurfaceBlockProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const isNear = useNearViewport(sectionRef);

  const { data, error, isPending, isError } = useQuery({
    ...countryTrustQuery(countrySlug, locale),
    enabled: isNear,
  });

  const notComputed =
    isError && isApiError(error) && error.error?.code === "trust_not_found";

  if (!isNear || isPending) {
    return (
      <div ref={sectionRef}>
        <Skeleton lines={3} />
      </div>
    );
  }

  if (isError && !notComputed) {
    return (
      <div data-testid="trust-surface-error">
        <ErrorState error={isApiError(error) ? error : undefined} />
      </div>
    );
  }

  if (!data || notComputed) {
    return (
      <p
        className="text-c4 text-sm"
        data-testid="trust-surface-empty"
      >
        Данные о доверии к источникам ещё не вычислены для этой страны.
      </p>
    );
  }

  const contradictionLabel = (() => {
    const score = data.components?.contradiction_component;
    if (score === null || score === undefined) return "Неизвестно";
    const raw = 100 - score;
    if (raw < 30) return "Низкая";
    if (raw < 60) return "Средняя";
    return "Высокая";
  })();

  const accent = TRUST_LABEL_ACCENT[data.trust_label] ?? "gold";

  return (
    <div
      className="flex flex-col gap-5"
      data-testid="trust-surface-block"
    >
      <div className="flex flex-wrap items-center gap-6">
        {data.trust_score != null && (
          <ProgressRing
            value={Math.round(data.trust_score)}
            label={data.trust_label}
            size={128}
            accent={accent}
            active
            mode="static"
          />
        )}
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="default">Свежесть: {data.freshness_status}</Badge>
          {data.confidence && (
            <Badge variant="trust">Уверенность: {data.confidence}</Badge>
          )}
        </div>
      </div>
      <LastVerifiedAt date={data.last_verified_at ?? undefined} />
      <p
        className="text-c3 text-sm"
        data-testid="contradiction-context"
      >
        Противоречивость данных:{" "}
        <Badge variant="default">{contradictionLabel}</Badge>
      </p>
      <Link
        href="/methodology"
        className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
      >
        О методологии →
      </Link>
      <DisclaimerNotice text={data.disclaimer} />
    </div>
  );
}
