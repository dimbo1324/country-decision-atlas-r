import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteDocumentsListProps = {
  documents: RouteDetailResponse["documents"];
};

export function RouteDocumentsList({ documents }: RouteDocumentsListProps) {
  if (documents.length === 0) {
    return (
      <RouteEmptyState message="Документы для этого маршрута пока не указаны." />
    );
  }

  return (
    <ul className="routeDocuments">
      {documents.map((document) => (
        <li key={document.id}>
          <strong>{document.name}</strong>
          <span>{document.is_mandatory ? "Обязательный" : "По ситуации"}</span>
          {document.note && <p>{document.note}</p>}
        </li>
      ))}
    </ul>
  );
}
