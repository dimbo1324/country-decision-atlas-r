import { useTranslations } from "next-intl";

type AIRefusalStateProps = {
  message: string;
};

export function AIRefusalState({ message }: AIRefusalStateProps) {
  const t = useTranslations("aiRefusalState");
  return (
    <div
      className="border-terra2/60 text-terra3 flex flex-col gap-1 border px-4 py-3"
      data-testid="ai-refusal"
    >
      <span className="font-display text-sm font-semibold">{t("heading")}</span>
      <p className="text-sm leading-relaxed">{message}</p>
    </div>
  );
}
