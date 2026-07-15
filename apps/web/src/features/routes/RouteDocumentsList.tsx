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
    <ul className="grid gap-2.5">
      {documents.map((document) => (
        <li
          key={document.id}
          className="border-warm flex flex-col gap-1 border-b pb-2.5 text-sm last:border-b-0"
        >
          <strong className="text-c1">{document.name}</strong>
          <span className="text-c3 text-xs">
            {document.is_mandatory ? "Обязательный" : "По ситуации"}
          </span>
          {document.note && (
            <p className="text-c3 text-xs leading-relaxed">{document.note}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
