import { getLocale, getTranslations } from "next-intl/server";
import { DataTable, Kicker } from "@country-decision-atlas/ui";
import { listMethodologyParameters } from "../../../../shared/api/methodology";
import { formatDate } from "../../../../shared/lib/format";
import { asSupportedLocale } from "../../../../shared/lib/locale";
import { DisclaimerNotice } from "../../../../shared/ui/DisclaimerNotice";
import { ErrorState } from "../../../../shared/ui/ErrorState";

export const dynamic = "force-dynamic";

function formatValue(value_numeric?: number | null, value_json?: unknown) {
  if (value_numeric != null) return String(value_numeric);
  if (value_json != null) return JSON.stringify(value_json);
  return "—";
}

export default async function MethodologyParametersPage() {
  const locale = asSupportedLocale(await getLocale());
  const t = await getTranslations("methodologyParametersPage");
  let response;
  try {
    response = await listMethodologyParameters();
  } catch {
    return (
      <div
        className="flex flex-col gap-6"
        data-testid="methodology-parameters-page"
      >
        <header className="flex flex-col gap-3">
          <Kicker>{t("kicker")}</Kicker>
          <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
        </header>
        <ErrorState error={t("loadError")} />
      </div>
    );
  }

  const rows = response.items.map((item) => [
    <span
      key="param"
      className="font-mono text-[11px]"
    >
      {item.param_key}
    </span>,
    formatValue(item.value_numeric, item.value_json),
    item.description,
    formatDate(item.effective_from, locale),
  ]);

  return (
    <div
      className="flex flex-col gap-6"
      data-testid="methodology-parameters-page"
    >
      <header className="flex flex-col gap-3">
        <Kicker>{t("kickerVersioned", { version: response.version })}</Kicker>
        <h1 className="font-display text-4xl font-bold">{t("title")}</h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          {t("description")}
        </p>
      </header>
      <DataTable
        columns={[
          { header: t("columnParameter") },
          { header: t("columnValue"), align: "right", numeric: true },
          { header: t("columnDescription") },
          { header: t("columnEffectiveFrom") },
        ]}
        rows={rows}
      />
      <DisclaimerNotice />
    </div>
  );
}
