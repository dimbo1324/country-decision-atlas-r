import Link from "next/link";

import type { LocaleCode } from "../../shared/api/countries";
import type { RouteDetailResponse } from "../../shared/api/routes";
import { routes } from "../../shared/lib/routes";
import { RouteDocumentsList } from "./RouteDocumentsList";
import { RouteEligibilityBadges } from "./RouteEligibilityBadges";
import { RouteEvidenceList } from "./RouteEvidenceList";
import { RouteSourcesList } from "./RouteSourcesList";

type RouteDetailViewProps = {
  route: RouteDetailResponse;
  locale: LocaleCode;
};

export function RouteDetailView({ route, locale }: RouteDetailViewProps) {
  return (
    <article className="routeDetail" data-testid="route-detail">
      <header className="pageHeader">
        <p className="eyebrow">Маршрут</p>
        <h1>{route.title}</h1>
        <div className="routeBadges">
          <span className="metaChip">{route.route_type}</span>
          <span className="metaChip">{route.legal_status}</span>
          <span className="metaChip">{route.status}</span>
        </div>
        <Link
          href={routes.countryWithLocale(route.country_slug, locale)}
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

      <section className="cardSection">
        <h2 className="cardSectionTitle">Документы</h2>
        <RouteDocumentsList documents={route.documents} />
      </section>

      <section className="cardSection">
        <h2 className="cardSectionTitle">Источники</h2>
        <RouteSourcesList sources={route.sources} />
      </section>

      <section className="cardSection">
        <h2 className="cardSectionTitle">Доказательства</h2>
        <RouteEvidenceList evidence={route.evidence} />
      </section>
    </article>
  );
}
