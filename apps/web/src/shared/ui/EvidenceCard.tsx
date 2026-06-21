import type { EvidenceItem } from "../api/evidence";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { LocalizationBadge } from "./LocalizationBadge";
import { formatDate } from "../lib/format";

type EvidenceCardProps = {
  item: EvidenceItem;
  sourceTitle?: string;
  sourceUrl?: string;
};

export function EvidenceCard({ item, sourceTitle, sourceUrl }: EvidenceCardProps) {
  const mainText = item.claim ?? item.title;
  return (
    <div className="evidenceCard" data-testid="evidence-card">
      {mainText && <p className="evidenceClaim">{mainText}</p>}
      {item.excerpt && (
        <blockquote className="evidenceExcerpt">{item.excerpt}</blockquote>
      )}
      <div className="metaRow evidenceMeta">
        {(item.confidence ?? item.confidence_level) && (
          <ConfidenceBadge confidence={item.confidence ?? item.confidence_level} />
        )}
        {item.evidence_type && (
          <span className="metaChip">{item.evidence_type.replace(/_/g, " ")}</span>
        )}
        {(item.retrieved_at ?? item.published_at) && (
          <span className="metaChip">
            {formatDate((item.retrieved_at ?? item.published_at) as string)}
          </span>
        )}
        <LocalizationBadge localization={item.localization} compact />
      </div>
      {(sourceTitle || sourceUrl || item.url) && (
        <div className="evidenceSourceRef">
          {sourceTitle && <span className="evidenceSourceTitle">{sourceTitle}</span>}
          {(sourceUrl ?? item.url) && (
            <a
              href={(sourceUrl ?? item.url) as string}
              target="_blank"
              rel="noreferrer"
              className="externalLink"
            >
              Открыть источник ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}
