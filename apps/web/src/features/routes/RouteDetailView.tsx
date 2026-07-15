import { Badge, Card, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";

import type { RouteDetailResponse, RouteType } from "../../shared/api/routes";
import { DisclaimerNotice } from "../../shared/ui/DisclaimerNotice";
import { routes } from "../../shared/lib/routes";
import { RouteMigrationBoardBlock } from "../migration-board";
import { RouteChecklistList } from "./RouteChecklistList";
import { RouteDocumentsList } from "./RouteDocumentsList";
import { RouteEligibilityBadges } from "./RouteEligibilityBadges";
import { RouteEvidenceList } from "./RouteEvidenceList";
import { RouteSourcesList } from "./RouteSourcesList";

const ROUTE_TYPE_LABELS: Record<RouteType, string> = {
  temporary_residence: "Временное проживание",
  permanent_residence: "ПМЖ",
  citizenship: "Гражданство",
  digital_nomad: "Digital nomad",
  work: "Работа",
  business: "Бизнес",
  study: "Учёба",
  investment: "Инвестиции",
};

const LEGAL_STATUS_LABELS: Record<string, string> = {
  proposed: "Предложен",
  adopted: "Принят",
  effective: "Действует",
  expired: "Истёк",
  revoked: "Отозван",
  unknown: "Статус неизвестен",
};

const STATUS_LABELS: Record<string, string> = {
  draft: "Черновик",
  review: "На проверке",
  published: "Опубликован",
  archived: "Архив",
  rejected: "Отклонён",
};

type RouteDetailViewProps = {
  route: RouteDetailResponse;
};

export function RouteDetailView({ route }: RouteDetailViewProps) {
  return (
    <article
      className="flex flex-col gap-6"
      data-testid="route-detail"
    >
      <header className="flex flex-col gap-3">
        <Kicker>Маршрут</Kicker>
        <h1 className="font-display text-4xl font-bold">{route.title}</h1>
        <div className="flex flex-wrap gap-2">
          <Badge variant="default">
            {ROUTE_TYPE_LABELS[route.route_type] ?? route.route_type}
          </Badge>
          <Badge variant="default">
            {LEGAL_STATUS_LABELS[route.legal_status] ?? route.legal_status}
          </Badge>
          <Badge variant="default">
            {STATUS_LABELS[route.status] ?? route.status}
          </Badge>
        </div>
        <Link
          href={routes.country(route.country_slug)}
          className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          Назад к стране
        </Link>
      </header>

      <div className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>Описание</Kicker>
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
          <Kicker>Параметры</Kicker>
          <dl className="flex flex-col gap-2.5">
            {route.income_requirement_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">Доход</dt>
                <dd className="text-c1 text-sm">
                  {route.income_requirement_note}
                </dd>
              </div>
            )}
            {route.fees_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">Сборы</dt>
                <dd className="text-c1 text-sm">{route.fees_note}</dd>
              </div>
            )}
            {route.processing_time_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">Срок обработки</dt>
                <dd className="text-c1 text-sm">
                  {route.processing_time_note}
                </dd>
              </div>
            )}
            {route.stay_period_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">Срок пребывания</dt>
                <dd className="text-c1 text-sm">{route.stay_period_note}</dd>
              </div>
            )}
            {route.renewal_note && (
              <div className="flex flex-col gap-0.5">
                <dt className="text-c3 text-xs font-bold">Продление</dt>
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
          <Kicker>Предупреждения</Kicker>
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
          <Kicker>Практический чек-лист</Kicker>
          <RouteChecklistList
            checklist={route.checklist}
            sources={route.sources}
            evidence={route.evidence}
          />
          {route.checklist.length > 0 && (
            <DisclaimerNotice text="Чек-лист носит справочный характер и не заменяет консультацию специалиста." />
          )}
        </Card>
      </div>

      <div data-testid="route-documents-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>Документы</Kicker>
          <RouteDocumentsList documents={route.documents} />
        </Card>
      </div>

      <div data-testid="route-migration-board-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>Люди, рассматривающие этот маршрут</Kicker>
          <RouteMigrationBoardBlock routeId={route.id} />
        </Card>
      </div>

      <div data-testid="route-sources-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>Источники</Kicker>
          <RouteSourcesList sources={route.sources} />
        </Card>
      </div>

      <div data-testid="route-evidence-section">
        <Card
          interactive={false}
          className="flex flex-col gap-3"
        >
          <Kicker>Доказательства</Kicker>
          <RouteEvidenceList evidence={route.evidence} />
        </Card>
      </div>
    </article>
  );
}
