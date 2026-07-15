import { Badge, Card } from "@country-decision-atlas/ui";
import type { EvidenceItem } from "../api/evidence";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { LocalizationBadge } from "./LocalizationBadge";
import { formatDate } from "../lib/format";
import { ArrowExternal } from "./LinkArrow";

type EvidenceCardProps = {
  item: EvidenceItem;
  sourceTitle?: string;
  sourceUrl?: string;
};

export function EvidenceCard({
  item,
  sourceTitle,
  sourceUrl,
}: EvidenceCardProps) {
  const mainText = item.claim ?? item.title;
  return (
    <div data-testid="evidence-card">
      <Card
        interactive={false}
        className="flex flex-col gap-2"
      >
        {mainText && (
          <p className="text-c1 text-sm leading-relaxed">{mainText}</p>
        )}
        {item.excerpt && (
          <blockquote className="border-warm text-c2 border-l-4 pl-3 text-sm italic">
            {item.excerpt}
          </blockquote>
        )}
        <div className="flex flex-wrap items-center gap-2">
          {(item.confidence ?? item.confidence_level) && (
            <ConfidenceBadge
              confidence={item.confidence ?? item.confidence_level}
            />
          )}
          {item.evidence_type && (
            <Badge variant="default">
              {item.evidence_type.replace(/_/g, " ")}
            </Badge>
          )}
          {(item.retrieved_at ?? item.published_at) && (
            <Badge variant="default">
              {formatDate((item.retrieved_at ?? item.published_at) as string)}
            </Badge>
          )}
          <LocalizationBadge
            localization={item.localization}
            compact
          />
        </div>
        {(sourceTitle || sourceUrl || item.url) && (
          <div className="flex flex-wrap items-center gap-2">
            {sourceTitle && (
              <span className="text-c2 text-sm font-medium">{sourceTitle}</span>
            )}
            {(sourceUrl ?? item.url) && (
              <a
                href={(sourceUrl ?? item.url) as string}
                target="_blank"
                rel="noreferrer"
                className="text-c1 hover:text-gold3 underline decoration-dotted underline-offset-2 transition-colors duration-200"
              >
                Открыть источник <ArrowExternal />
              </a>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
