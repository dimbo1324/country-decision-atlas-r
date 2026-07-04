import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteEvidenceListProps = {
  evidence: RouteDetailResponse["evidence"];
};

export function RouteEvidenceList({ evidence }: RouteEvidenceListProps) {
  if (evidence.length === 0) {
    return (
      <RouteEmptyState message="Доказательства для этого маршрута пока не указаны." />
    );
  }

  return (
    <div className="routeEvidence">
      {evidence.map((item) => (
        <article key={item.id}>
          <strong>{item.claim ?? item.source_title ?? "Доказательство"}</strong>
          {item.excerpt && <p>{item.excerpt}</p>}
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noreferrer"
            >
              {item.source_title ?? item.source_url}
            </a>
          )}
        </article>
      ))}
    </div>
  );
}
