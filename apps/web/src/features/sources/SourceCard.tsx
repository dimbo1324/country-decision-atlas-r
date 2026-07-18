import { Badge, Card } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { CountryListResponse } from "../../shared/api/countries";
import type { SourceListResponse } from "../../shared/api/sources";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { ArrowNext, ArrowExternal } from "../../shared/ui/LinkArrow";

type Source = SourceListResponse["items"][number];

export function SourceCard({
  source,
  country,
  onShowEvidence,
}: {
  source: Source;
  country: CountryListResponse["items"][number] | undefined;
  onShowEvidence: (sourceId: string, title: string) => void;
}) {
  const locale = useAppLocale();
  return (
    <div data-testid="source-card">
      <Card
        interactive={false}
        className="flex flex-col gap-3"
      >
        <div className="flex flex-wrap items-start justify-between gap-2">
          <span className="font-display text-base font-semibold">
            {source.title}
          </span>
          <div className="flex items-center gap-2">
            {source.source_type && (
              <Badge variant="info">{source.source_type}</Badge>
            )}
            {source.status && <StatusBadge status={source.status} />}
            <LocalizationBadge
              localization={source.localization}
              compact
            />
          </div>
        </div>
        {source.publisher && (
          <span className="text-c4 text-xs">{source.publisher}</span>
        )}
        <div className="flex flex-wrap gap-2">
          {source.confidence && (
            <ConfidenceBadge confidence={source.confidence} />
          )}
          {source.language && (
            <Badge variant="default">{source.language}</Badge>
          )}
          {source.last_checked_at && (
            <Badge variant="default">
              Проверено: {formatDate(source.last_checked_at, locale)}
            </Badge>
          )}
          {source.published_at && (
            <Badge variant="default">
              Опубликовано: {formatDate(source.published_at, locale)}
            </Badge>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-4 text-sm">
          <a
            href={source.url}
            target="_blank"
            rel="noreferrer"
            data-testid="source-external-link"
            className="text-gold3 hover:text-gold transition-colors duration-300"
          >
            Открыть источник <ArrowExternal />
          </a>
          {country && (
            <Link
              href={routes.country(country.slug)}
              className="text-c3 hover:text-c1 transition-colors duration-300"
            >
              Страна: {country.name} <ArrowNext />
            </Link>
          )}
          <button
            type="button"
            onClick={() => onShowEvidence(source.id, source.title)}
            data-testid="source-evidence-toggle"
            className="font-mono text-c3 hover:text-gold3 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300"
          >
            Доказательства <ArrowNext />
          </button>
        </div>
      </Card>
    </div>
  );
}
