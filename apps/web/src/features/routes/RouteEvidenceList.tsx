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
    <div className="grid gap-2.5">
      {evidence.map((item) => (
        <article
          key={item.id}
          className="border-warm flex flex-col gap-1 border-b pb-2.5 text-sm last:border-b-0"
        >
          <strong className="text-c1">
            {item.claim ?? item.source_title ?? "Доказательство"}
          </strong>
          {item.excerpt && (
            <p className="text-c3 text-xs leading-relaxed">{item.excerpt}</p>
          )}
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-gold3 hover:text-gold text-xs transition-colors duration-200"
            >
              {item.source_title ?? item.source_url}
            </a>
          )}
        </article>
      ))}
    </div>
  );
}
