import { useTranslations } from "next-intl";
import { Badge } from "@country-decision-atlas/ui";
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
  const t = useTranslations("routeDetail");

  if (checklist.length === 0) {
    return <RouteEmptyState message={t("noChecklist")} />;
  }

  const sorted = [...checklist].sort((a, b) => a.step_order - b.step_order);

  return (
    <ol
      className="flex flex-col gap-3"
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
            className="border-warm flex flex-col gap-1.5 border-b pb-3 last:border-b-0 last:pb-0"
            data-testid="route-checklist-item"
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-c4 font-mono text-xs">
                {item.step_order}
              </span>
              <strong className="text-c1 text-sm">{item.title}</strong>
              <Badge variant="default">
                {item.is_required ? t("required") : t("situational")}
              </Badge>
            </div>
            {item.description && (
              <p className="text-c2 text-sm leading-relaxed">
                {item.description}
              </p>
            )}
            {item.document_note && (
              <p className="text-c3 text-xs">
                {t("documentsNote", { note: item.document_note })}
              </p>
            )}
            {item.cost_note && (
              <p className="text-c3 text-xs">
                {t("costNote", { note: item.cost_note })}
              </p>
            )}
            {item.timing_note && (
              <p className="text-c3 text-xs">
                {t("timingNote", { note: item.timing_note })}
              </p>
            )}
            {item.official_requirement_note && (
              <p className="text-c3 text-xs">
                {t("officialRequirementNote", {
                  note: item.official_requirement_note,
                })}
              </p>
            )}
            {linkedSource && (
              <a
                href={linkedSource.url}
                target="_blank"
                rel="noreferrer"
                className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
                data-testid="route-checklist-source-link"
              >
                {t("source", { title: linkedSource.title })}
              </a>
            )}
            {!linkedSource && linkedEvidence?.source_url && (
              <a
                href={linkedEvidence.source_url}
                target="_blank"
                rel="noreferrer"
                className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
                data-testid="route-checklist-source-link"
              >
                {t("source", {
                  title:
                    linkedEvidence.source_title ?? linkedEvidence.source_url,
                })}
              </a>
            )}
          </li>
        );
      })}
    </ol>
  );
}
