import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";

type CountryProfileSectionsProps = {
  profile: CountryReadModelResponse["profile"];
  skipExecutiveSummary?: boolean;
};

const SECTIONS: {
  key: keyof NonNullable<CountryReadModelResponse["profile"]>;
  label: string;
}[] = [
  { key: "executive_summary", label: "Overview" },
  { key: "migration_overview", label: "Migration / Residence" },
  { key: "tax_overview", label: "Tax" },
  { key: "cost_of_living_overview", label: "Cost of living" },
  { key: "business_overview", label: "Business" },
  { key: "safety_overview", label: "Safety" },
  { key: "legal_signals_summary", label: "Legal signals" },
  { key: "risk_summary", label: "Risks" },
  { key: "source_summary", label: "Sources" },
];

export function CountryProfileSections({
  profile,
  skipExecutiveSummary = false,
}: CountryProfileSectionsProps) {
  if (!profile) return <EmptyState message="No profile data available." />;

  const filled = SECTIONS.filter(
    (s) => profile[s.key] && !(skipExecutiveSummary && s.key === "executive_summary"),
  );
  if (filled.length === 0) return <EmptyState message="No profile sections available." />;

  return (
    <div className="sectionStack">
      {filled.map((s) => (
        <div key={s.key} className="profileSection">
          <h3 className="sectionTitle">{s.label}</h3>
          <p>{profile[s.key]}</p>
        </div>
      ))}
    </div>
  );
}
