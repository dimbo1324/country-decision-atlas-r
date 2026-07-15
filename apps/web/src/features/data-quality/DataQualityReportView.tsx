import Link from "next/link";
import { Badge, Card, DataTable, Kicker } from "@country-decision-atlas/ui";
import type { DataQualityReport } from "../../shared/api/data-quality";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { StatusBadge } from "../../shared/ui/StatusBadge";

interface Props {
  report: DataQualityReport;
}

export function DataQualityReportView({ report }: Props) {
  return (
    <div
      className="flex flex-col gap-8"
      data-testid="data-quality-report"
    >
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>Статус</Kicker>
          <StatusBadge status={report.overall_status} />
        </Card>
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>Критические проблемы</Kicker>
          <span className="font-display text-2xl font-bold">
            {report.critical_issues_count}
          </span>
        </Card>
        <Card
          interactive={false}
          className="flex flex-col gap-2"
        >
          <Kicker>Предупреждения</Kicker>
          <span className="font-display text-2xl font-bold">
            {report.warnings_count}
          </span>
        </Card>
        {report.checked_at && (
          <Card
            interactive={false}
            className="flex flex-col gap-2"
          >
            <Kicker>Проверено</Kicker>
            <span className="text-c2 text-sm">
              {formatDate(report.checked_at)}
            </span>
          </Card>
        )}
      </div>

      {report.checks && report.checks.length > 0 && (
        <div className="flex flex-col gap-3">
          <Kicker>Проверки</Kicker>
          <DataTable
            columns={[{ header: "Код" }, { header: "Статус" }]}
            rows={report.checks.map((check) => [
              check.code,
              <StatusBadge
                key={check.code}
                status={check.status}
              />,
            ])}
          />
        </div>
      )}

      <div className="flex flex-col gap-3">
        <Kicker>Проблемы ({report.issues?.length ?? 0})</Kicker>
        {!report.issues || report.issues.length === 0 ? (
          <EmptyState message="Проблем качества данных не найдено." />
        ) : (
          <div className="flex flex-col gap-3">
            {report.issues.map((issue, i) => (
              <Card
                key={`${issue.code}-${i}`}
                interactive={false}
                className="flex flex-col gap-2"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-c3 text-xs">
                    {issue.code}
                  </span>
                  <StatusBadge status={issue.severity} />
                  <Badge variant="default">{issue.entity_type}</Badge>
                  {issue.entity_id && (
                    <span className="text-c4 font-mono text-xs">
                      {issue.entity_id}
                    </span>
                  )}
                </div>
                <p className="text-c2 text-sm leading-relaxed">
                  {issue.message}
                </p>
              </Card>
            ))}
          </div>
        )}
      </div>

      <div>
        <Link
          href={routes.countries}
          className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          ← Назад к странам
        </Link>
      </div>
    </div>
  );
}
