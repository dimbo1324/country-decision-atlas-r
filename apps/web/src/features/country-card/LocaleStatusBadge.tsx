import { Badge } from "@country-decision-atlas/ui";
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
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">Запрошенный язык:</span>
        <Badge variant="default">{locale.requested_locale}</Badge>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">Фактически показанный язык:</span>
        <Badge variant="default">{locale.resolved_locale}</Badge>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-c3 text-sm">Статус перевода:</span>
        <Badge variant={isFallback ? "warning" : "default"}>
          {STATUS_LABELS[locale.translation_status] ??
            locale.translation_status}
        </Badge>
      </div>
      {isFallback && locale.requested_locale === "ru" && (
        <p className="text-terra3 font-quote text-sm italic">
          Русский перевод частично отсутствует. Показана английская резервная
          версия.
        </p>
      )}
    </div>
  );
}
