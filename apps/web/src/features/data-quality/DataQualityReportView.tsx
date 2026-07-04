import Link from "next/link";
import type { DataQualityReport } from "../../shared/api/data-quality";
import { routes } from "../../shared/lib/routes";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";
import { StatusBadge } from "../../shared/ui/StatusBadge";
import { SummaryCard } from "../../shared/ui/SummaryCard";
import { SectionHeader } from "../../shared/ui/SectionHeader";

interface Props {
  report: DataQualityReport;
}

export function DataQualityReportView({ report }: Props) {
  return (
    <div
      className="dqWrap"
      data-testid="data-quality-report"
    >
      <div className="analyticalSummaryRow">
        <SummaryCard
          label="Статус"
          value={report.overall_status}
          detail={report.valid ? "данные готовы" : "обнаружены проблемы"}
        />
        <SummaryCard
          label="Критические проблемы"
          value={report.critical_issues_count}
        />
        <SummaryCard
          label="Предупреждения"
          value={report.warnings_count}
        />
        {report.checked_at && (
          <SummaryCard
            label="Проверено"
            value={formatDate(report.checked_at)}
          />
        )}
      </div>

      <div className="dqStatusRow">
        <StatusBadge status={report.overall_status} />
        {report.valid && <StatusBadge status="valid" />}
      </div>

      {report.checks && report.checks.length > 0 && (
        <section className="cardSection">
          <SectionHeader
            title="Проверки"
            eyebrow="Проверки качества"
          />
          <div className="checkList">
            {report.checks.map((check) => (
              <div
                key={check.code}
                className="checkCard"
              >
                <span className="checkCode">{check.code}</span>
                <StatusBadge status={check.status} />
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="cardSection">
        <SectionHeader
          title={`Проблемы (${report.issues?.length ?? 0})`}
          eyebrow="Проблемы качества данных"
        />
        {!report.issues || report.issues.length === 0 ? (
          <EmptyState message="Проблем качества данных не найдено." />
        ) : (
          <div className="dqIssueList">
            {report.issues.map((issue, i) => (
              <div
                key={`${issue.code}-${i}`}
                className={`dqIssueCard dqSeverity-${issue.severity}`}
              >
                <div className="dqIssueHeader">
                  <span className="dqIssueCode">{issue.code}</span>
                  <StatusBadge status={issue.severity} />
                  <span className="metaChip">{issue.entity_type}</span>
                  {issue.entity_id && (
                    <span className="dqEntityId">{issue.entity_id}</span>
                  )}
                </div>
                <p className="dqIssueMessage">{issue.message}</p>
              </div>
            ))}
          </div>
        )}
      </section>

      <div className="entityLinkRow">
        <Link
          href={routes.countries}
          className="internalLink"
        >
          ← Назад к странам
        </Link>
      </div>
    </div>
  );
}
