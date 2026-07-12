import { Link } from "../../i18n/navigation";

import type { RouteListItem } from "../../shared/api/routes";
import { routeDetailPath } from "./route-links";
import { RouteEligibilityBadges } from "./RouteEligibilityBadges";

type RouteCardProps = {
  route: RouteListItem;
};

export function RouteCard({ route }: RouteCardProps) {
  return (
    <article
      className="routeCard"
      data-testid="route-card"
    >
      <div className="routeCardHeader">
        <div>
          <h3>{route.title}</h3>
          <div className="routeBadges">
            <span className="metaChip">{route.route_type}</span>
            <span className="metaChip">{route.legal_status}</span>
          </div>
        </div>
        <Link
          href={routeDetailPath(route.id)}
          className="internalLink"
        >
          Открыть
        </Link>
      </div>
      {route.summary && <p>{route.summary}</p>}
      {route.eligibility_summary && (
        <p className="routeEligibilitySummary">{route.eligibility_summary}</p>
      )}
      <RouteEligibilityBadges
        eligibility={route.eligibility}
        compact
      />
    </article>
  );
}
