import type { DataQualityReport } from "../../shared/api/data-quality";
import { formatDate } from "../../shared/lib/format";
import { EmptyState } from "../../shared/ui/EmptyState";

interface Props {
  report: DataQualityReport;
}

export function DataQualityReportView({ report }: Props) {
  return (
    <div className="dqWrap">
      <div className="dqSummaryRow">
        <div className="dqSummaryCard">
          <span className="dqLabel">Status</span>
          <span className="dqValue">{report.overall_status}</span>
        </div>
        <div className="dqSummaryCard">
          <span className="dqLabel">Critical issues</span>
          <span className="dqValue dqCritical">
            {report.critical_issues_count}
          </span>
        </div>
        <div className="dqSummaryCard">
          <span className="dqLabel">Warnings</span>
          <span className="dqValue dqWarning">{report.warnings_count}</span>
        </div>
        {report.checked_at && (
          <div className="dqSummaryCard">
            <span className="dqLabel">Checked at</span>
            <span className="dqValue">{formatDate(report.checked_at)}</span>
          </div>
        )}
      </div>

      {report.issues && report.issues.length > 0 ? (
        <div className="dqIssueList">
          <h2 className="dqSectionTitle">Issues ({report.issues.length})</h2>
          {report.issues.map((issue, i) => (
            <div
              key={`${issue.code}-${i}`}
              className={`dqIssueCard dqSeverity-${issue.severity}`}
            >
              <div className="dqIssueHeader">
                <span className="dqIssueCode">{issue.code}</span>
                <span className="metaChip">{issue.severity}</span>
                <span className="metaChip">{issue.entity_type}</span>
                {issue.entity_id && (
                  <span className="dqEntityId">{issue.entity_id}</span>
                )}
              </div>
              <p className="dqIssueMessage">{issue.message}</p>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState />
      )}
    </div>
  );
}
