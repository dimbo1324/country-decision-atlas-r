import { useTranslations } from "next-intl";
import type { RouteDetailResponse } from "../../shared/api/routes";
import { RouteEmptyState } from "./RouteEmptyState";

type RouteSourcesListProps = {
  sources: RouteDetailResponse["sources"];
};

export function RouteSourcesList({ sources }: RouteSourcesListProps) {
  const t = useTranslations("routeDetail");

  if (sources.length === 0) {
    return <RouteEmptyState message={t("noSources")} />;
  }

  return (
    <div className="grid gap-2.5">
      {sources.map((source) => (
        <a
          key={source.id}
          href={source.url}
          target="_blank"
          rel="noreferrer"
          className="border-warm flex flex-col gap-1 border-b pb-2.5 text-sm last:border-b-0"
        >
          <strong className="text-c1 hover:text-gold3 transition-colors duration-200">
            {source.title}
          </strong>
          <span className="text-c3 text-xs">
            {[source.source_type, source.publisher, source.confidence]
              .filter(Boolean)
              .join(" · ")}
          </span>
        </a>
      ))}
    </div>
  );
}
