import { useTranslations } from "next-intl";
import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";

import type { RouteDetailResponse } from "../../shared/api/routes";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { routes } from "../../shared/lib/routes";
import { RouteMigrationBoardBlock } from "../migration-board";
import { ROUTE_TYPE_LABELS } from "./route-labels";
import { RouteChecklistList } from "./RouteChecklistList";
import { RouteDocumentsList } from "./RouteDocumentsList";
import { RouteEligibilityBadges } from "./RouteEligibilityBadges";
import { RouteEvidenceList } from "./RouteEvidenceList";
import { RouteSourcesList } from "./RouteSourcesList";

const LEGAL_STATUS_LABEL_KEYS: Record<string, string> = {
  proposed: "legalStatusProposed",
  adopted: "legalStatusAdopted",
  effective: "legalStatusEffective",
  expired: "legalStatusExpired",
  revoked: "legalStatusRevoked",
  unknown: "legalStatusUnknown",
};

const STATUS_LABEL_KEYS: Record<string, string> = {
  draft: "statusDraft",
  review: "statusReview",
  published: "statusPublished",
  archived: "statusArchived",
  rejected: "statusRejected",
};

type RouteDetailViewProps = {
  route: RouteDetailResponse;
};

export function RouteDetailView({ route }: RouteDetailViewProps) {
  const t = useTranslations("routeDetail");
  const locale = useAppLocale();

  const legalStatusKey = LEGAL_STATUS_LABEL_KEYS[route.legal_status];
  const statusKey = STATUS_LABEL_KEYS[route.status];

  return (
    <article
      className="flex flex-col gap-6"
      data-testid="route-detail"
    >
      <header className="flex flex-col gap-3">
        <Kicker>{t("route")}</Kicker>
        <h1 className="font-display text-4xl font-bold">{route.title}</h1>
        <div className="flex flex-wrap gap-2">
          <Badge variant="default">
            {ROUTE_TYPE_LABELS[locale][route.route_type] ?? route.route_type}
          </Badge>
          <Badge variant="default">
            {legalStatusKey ? t(legalStatusKey) : route.legal_status}
          </Badge>
          <Badge variant="default">
            {statusKey ? t(statusKey) : route.status}
          </Badge>
        </div>
        <Link
          href={routes.country(route.country_slug)}
          className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          {t("backToCountry")}
        </Link>
      </header>

      <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>{t("description")}</Kicker>
          {route.summary && (
            <p className="text-c1 text-sm leading-relaxed">{route.summary}</p>
          )}
          {route.eligibility_summary && (
            <p className="text-c1 text-sm leading-relaxed">
              {route.eligibility_summary}
            </p>
          )}
          <RouteEligibilityBadges eligibility={route.eligibility} />
        </Card>

        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>{t("parameters")}</Kicker>
          <dl className="flex flex-col gap-2.5">
            {route.income_requirement_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">{t("income")}</dt>
                <dd className="text-c1 text-sm">
                  {route.income_requirement_note}
                </dd>
              </div>
            )}
            {route.fees_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">{t("fees")}</dt>
                <dd className="text-c1 text-sm">{route.fees_note}</dd>
              </div>
            )}
            {route.processing_time_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">
                  {t("processingTime")}
                </dt>
                <dd className="text-c1 text-sm">
                  {route.processing_time_note}
                </dd>
              </div>
            )}
            {route.stay_period_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">{t("stayPeriod")}</dt>
                <dd className="text-c1 text-sm">{route.stay_period_note}</dd>
              </div>
            )}
            {route.renewal_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">{t("renewal")}</dt>
                <dd className="text-c1 text-sm">{route.renewal_note}</dd>
              </div>
            )}
          </dl>
        </Card>
      </div>

      {(route.tax_warning || route.legal_warning) && (
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>{t("warnings")}</Kicker>
          <div className="flex flex-col gap-2">
            {route.tax_warning && (
              <p className="border-gold3 text-c1 border-l-4 pl-2.5 text-sm">
                {route.tax_warning}
              </p>
            )}
            {route.legal_warning && (
              <p className="border-gold3 text-c1 border-l-4 pl-2.5 text-sm">
                {route.legal_warning}
              </p>
            )}
          </div>
        </Card>
      )}

      <div data-testid="route-checklist-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>{t("checklist")}</Kicker>
          <RouteChecklistList
            checklist={route.checklist}
            sources={route.sources}
            evidence={route.evidence}
          />
          {route.checklist.length > 0 && (
            <DisclaimerNotice text={t("checklistDisclaimer")} />
          )}
        </Card>
      </div>

      <div data-testid="route-documents-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>{t("documents")}</Kicker>
          <RouteDocumentsList documents={route.documents} />
        </Card>
      </div>

      <div data-testid="route-migration-board-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>{t("peopleConsidering")}</Kicker>
          <RouteMigrationBoardBlock routeId={route.id} />
        </Card>
      </div>

      <div data-testid="route-sources-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>{t("sources")}</Kicker>
          <RouteSourcesList sources={route.sources} />
        </Card>
      </div>

      <div data-testid="route-evidence-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>{t("evidence")}</Kicker>
          <RouteEvidenceList evidence={route.evidence} />
        </Card>
      </div>
    </article>
  );
}
