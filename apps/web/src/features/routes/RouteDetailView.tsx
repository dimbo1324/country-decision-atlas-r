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
      className="routeDetail"
      data-testid="route-detail"
    >
      <header className="pageHeader">
        <p className="eyebrow">Маршрут</p>
        <h1>{route.title}</h1>
        <div className="routeBadges">
          <span className="metaChip">
            {ROUTE_TYPE_LABELS[route.route_type] ?? route.route_type}
          </span>
          <span className="metaChip">
            {LEGAL_STATUS_LABELS[route.legal_status] ?? route.legal_status}
          </span>
          <span className="metaChip">
            {STATUS_LABELS[route.status] ?? route.status}
          </span>
        </div>
        <Link
          href={routes.country(route.country_slug)}
          className="internalLink"
        >
          Назад к стране
        </Link>
      </header>

      <div className="routeDetailGrid">
        <section className="cardSection cardSectionHighlight">
          <h2 className="cardSectionTitle">Описание</h2>
          {route.summary && <p>{route.summary}</p>}
          {route.eligibility_summary && <p>{route.eligibility_summary}</p>}
          <RouteEligibilityBadges eligibility={route.eligibility} />
        </section>

        <section className="cardSection">
          <h2 className="cardSectionTitle">Параметры</h2>
          <dl className="routeFacts">
            {route.income_requirement_note && (
              <div>
                <dt>Доход</dt>
                <dd>{route.income_requirement_note}</dd>
              </div>
            )}
            {route.fees_note && (
              <div>
                <dt>Сборы</dt>
                <dd>{route.fees_note}</dd>
              </div>
            )}
            {route.processing_time_note && (
              <div>
                <dt>Срок обработки</dt>
                <dd>{route.processing_time_note}</dd>
              </div>
            )}
            {route.stay_period_note && (
              <div>
                <dt>Срок пребывания</dt>
                <dd>{route.stay_period_note}</dd>
              </div>
            )}
            {route.renewal_note && (
              <div>
                <dt>Продление</dt>
                <dd>{route.renewal_note}</dd>
              </div>
            )}
          </dl>
        </section>
      </div>

      {(route.tax_warning || route.legal_warning) && (
        <section className="cardSection">
          <h2 className="cardSectionTitle">Предупреждения</h2>
          <div className="routeWarnings">
            {route.tax_warning && <p>{route.tax_warning}</p>}
            {route.legal_warning && <p>{route.legal_warning}</p>}
          </div>
        </section>
      )}

      <section
        className="cardSection"
        data-testid="route-checklist-section"
      >
        <h2 className="cardSectionTitle">Практический чек-лист</h2>
        <RouteChecklistList
          checklist={route.checklist}
          sources={route.sources}
          evidence={route.evidence}
        />
        {route.checklist.length > 0 && (
          <DisclaimerNotice text="Чек-лист носит справочный характер и не заменяет консультацию специалиста." />
        )}
      </section>

      <section
        className="cardSection"
        data-testid="route-documents-section"
      >
        <h2 className="cardSectionTitle">Документы</h2>
        <RouteDocumentsList documents={route.documents} />
      </section>

      <section
        className="cardSection"
        data-testid="route-migration-board-section"
      >
        <h2 className="cardSectionTitle">Люди, рассматривающие этот маршрут</h2>
        <RouteMigrationBoardBlock routeId={route.id} />
      </section>

      <section
        className="cardSection"
        data-testid="route-sources-section"
      >
        <h2 className="cardSectionTitle">Источники</h2>
        <RouteSourcesList sources={route.sources} />
      </section>

      <section
        className="cardSection"
        data-testid="route-evidence-section"
      >
        <h2 className="cardSectionTitle">Доказательства</h2>
        <RouteEvidenceList evidence={route.evidence} />
      </section>
    </article>
  );
}
