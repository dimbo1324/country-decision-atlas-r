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
    <div className="dqWrap" data-testid="data-quality-report">
      <div className="analyticalSummaryRow">
        <SummaryCard
          label="Status"
          value={report.overall_status}
          detail={report.valid ? "dataset ready" : "issues found"}
        />
        <SummaryCard
          label="Critical issues"
          value={report.critical_issues_count}
        />
        <SummaryCard label="Warnings" value={report.warnings_count} />
        {report.checked_at && (
          <SummaryCard
            label="Checked at"
            value={formatDate(report.checked_at)}
          />
        )}
      </div>

      <div className="dqStatusRow">
        <StatusBadge status={report.overall_status} />
        {report.valid && (
          <StatusBadge status="valid" />
        )}
      </div>

      {report.checks && report.checks.length > 0 && (
        <section className="cardSection">
          <SectionHeader title="Checks" eyebrow="Quality checks" />
          <div className="checkList">
            {report.checks.map((check) => (
              <div key={check.code} className="checkCard">
                <span className="checkCode">{check.code}</span>
                <StatusBadge status={check.status} />
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="cardSection">
        <SectionHeader
          title={`Issues (${report.issues?.length ?? 0})`}
          eyebrow="Data quality issues"
        />
        {!report.issues || report.issues.length === 0 ? (
          <EmptyState message="No data-quality issues found. The MVP dataset is ready for frontend usage." />
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
        <Link href={routes.countries} className="internalLink">
          ← Back to countries
        </Link>
      </div>
    </div>
  );
}
