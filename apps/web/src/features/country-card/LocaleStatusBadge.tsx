import type { CountryReadModelResponse } from "../../shared/api/countries";

type LocaleStatusBadgeProps = {
  locale: CountryReadModelResponse["locale"];
};

const STATUS_LABELS: Record<string, string> = {
  source: "Source language",
  translated: "Translated",
  fallback: "Fallback",
  missing: "Missing translation",
};

export function LocaleStatusBadge({ locale }: LocaleStatusBadgeProps) {
  const isFallback = locale.translation_status === "fallback";

  return (
    <div className="localeStatusBlock">
      <div className="localeStatusRow">
        <span>Requested locale:</span>
        <span className="metaChip">{locale.requested_locale}</span>
      </div>
      <div className="localeStatusRow">
        <span>Resolved locale:</span>
        <span className="metaChip">{locale.resolved_locale}</span>
      </div>
      <div className="localeStatusRow">
        <span>Translation status:</span>
        <span className={`metaChip${isFallback ? " metaChipWarn" : ""}`}>
          {STATUS_LABELS[locale.translation_status] ?? locale.translation_status}
        </span>
      </div>
      {isFallback && locale.requested_locale === "ru" && (
        <p className="localeNotice">
          Русский перевод частично отсутствует. Показана английская fallback-версия.
        </p>
      )}
    </div>
  );
}
