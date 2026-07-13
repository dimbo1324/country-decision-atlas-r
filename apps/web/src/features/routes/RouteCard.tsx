import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { RouteListItem } from "../../shared/api/routes";
import { routeDetailPath } from "./route-links";
import { RouteEligibilityBadges } from "./RouteEligibilityBadges";

type RouteCardProps = {
  route: RouteListItem;
};

export function RouteCard({ route }: RouteCardProps) {
  return (
    <div data-testid="route-card">
    <Card
      interactive={false}
      className="flex flex-col gap-3"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-2">
          <h3 className="font-display text-base font-semibold">{route.title}</h3>
          <div className="flex flex-wrap gap-2">
            <Badge variant="default">{route.route_type}</Badge>
            <Badge variant="default">{route.legal_status}</Badge>
          </div>
        </div>
        <Link
          href={routeDetailPath(route.id)}
          className="font-mono text-gold3 hover:text-gold shrink-0 text-[9px] tracking-[0.15em] uppercase transition-colors duration-300"
        >
          Открыть
        </Link>
      </div>
      {route.summary && (
        <p className="text-c3 text-sm leading-relaxed">{route.summary}</p>
      )}
      {route.eligibility_summary && (
        <p className="text-c4 text-xs italic">{route.eligibility_summary}</p>
      )}
      <RouteEligibilityBadges
        eligibility={route.eligibility}
        compact
      />
    </Card>
    </div>
  );
}
