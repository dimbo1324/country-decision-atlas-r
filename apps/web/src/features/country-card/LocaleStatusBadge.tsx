import type { CountryReadModelResponse } from "../../shared/api/countries";

type LocaleStatusBadgeProps = {
  locale: CountryReadModelResponse["locale"];
};

const STATUS_LABELS: Record<string, string> = {
  source: "Исходный язык",
  translated: "Переведено",
  fallback: "Резервная версия",
  missing: "Перевод отсутствует",
};

export function LocaleStatusBadge({ locale }: LocaleStatusBadgeProps) {
  const isFallback = locale.translation_status === "fallback";

  return (
    <div className="localeStatusBlock">
      <div className="localeStatusRow">
        <span>Запрошенный язык:</span>
        <span className="metaChip">{locale.requested_locale}</span>
      </div>
      <div className="localeStatusRow">
        <span>Фактически показанный язык:</span>
        <span className="metaChip">{locale.resolved_locale}</span>
      </div>
      <div className="localeStatusRow">
        <span>Статус перевода:</span>
        <span className={`metaChip${isFallback ? " metaChipWarn" : ""}`}>
          {STATUS_LABELS[locale.translation_status] ?? locale.translation_status}
        </span>
      </div>
      {isFallback && locale.requested_locale === "ru" && (
        <p className="localeNotice">
          Русский перевод частично отсутствует. Показана английская резервная версия.
        </p>
      )}
    </div>
  );
}
