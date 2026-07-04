import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteChecklistListProps = {
  checklist: RouteDetailResponse["checklist"];
  sources: RouteDetailResponse["sources"];
  evidence: RouteDetailResponse["evidence"];
};

export function RouteChecklistList({
  checklist,
  sources,
  evidence,
}: RouteChecklistListProps) {
  if (checklist.length === 0) {
    return (
      <RouteEmptyState message="Практический чек-лист для этого маршрута пока не подготовлен." />
    );
  }

  const sorted = [...checklist].sort((a, b) => a.step_order - b.step_order);

  return (
    <ol
      className="routeChecklist"
      data-testid="route-checklist-list"
    >
      {sorted.map((item) => {
        const linkedSource = sources.find(
          (source) => source.id === item.source_id,
        );
        const linkedEvidence = evidence.find(
          (evidenceItem) => evidenceItem.id === item.evidence_item_id,
        );
        return (
          <li
            key={item.id}
            className="routeChecklistItem"
            data-testid="route-checklist-item"
          >
            <div className="routeChecklistItemHeader">
              <span className="routeChecklistStepOrder">{item.step_order}</span>
              <strong>{item.title}</strong>
              <span className="metaChip">
                {item.is_required ? "Обязательно" : "По ситуации"}
              </span>
            </div>
            {item.description && <p>{item.description}</p>}
            {item.document_note && (
              <p className="routeChecklistNote">
                Документы: {item.document_note}
              </p>
            )}
            {item.cost_note && (
              <p className="routeChecklistNote">Стоимость: {item.cost_note}</p>
            )}
            {item.timing_note && (
              <p className="routeChecklistNote">Сроки: {item.timing_note}</p>
            )}
            {item.official_requirement_note && (
              <p className="routeChecklistNote">
                Официальное требование: {item.official_requirement_note}
              </p>
            )}
            {linkedSource && (
              <a
                href={linkedSource.url}
                target="_blank"
                rel="noreferrer"
                data-testid="route-checklist-source-link"
              >
                Источник: {linkedSource.title}
              </a>
            )}
            {!linkedSource && linkedEvidence?.source_url && (
              <a
                href={linkedEvidence.source_url}
                target="_blank"
                rel="noreferrer"
                data-testid="route-checklist-source-link"
              >
                Источник:{" "}
                {linkedEvidence.source_title ?? linkedEvidence.source_url}
              </a>
            )}
          </li>
        );
      })}
    </ol>
  );
}
