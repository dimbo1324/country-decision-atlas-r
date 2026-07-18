import { useTranslations } from "next-intl";

type DecisionWeightSummaryProps = {
  sum: number;
};

export function DecisionWeightSummary({ sum }: DecisionWeightSummaryProps) {
  const t = useTranslations("decisionPersonalization");
  return (
    <div className="flex flex-col gap-1">
      <span className="text-c3 text-sm">{t("sumLabel", { sum })}</span>
      {sum === 0 && (
        <p
          role="alert"
          className="text-terra3 text-sm"
        >
          {t("sumZeroWarning")}
        </p>
      )}
    </div>
  );
}
