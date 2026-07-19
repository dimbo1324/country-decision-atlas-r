import { useTranslations } from "next-intl";
import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteDocumentsListProps = {
  documents: RouteDetailResponse["documents"];
};

export function RouteDocumentsList({ documents }: RouteDocumentsListProps) {
  const t = useTranslations("routeDetail");

  if (documents.length === 0) {
    return <RouteEmptyState message={t("noDocuments")} />;
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
            {document.is_mandatory ? t("required") : t("situational")}
          </span>
          {document.note && (
            <p className="text-c3 text-xs leading-relaxed">{document.note}</p>
          )}
        </li>
      ))}
    </ul>
  );
}
