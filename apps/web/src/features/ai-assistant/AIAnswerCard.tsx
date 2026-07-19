import { useTranslations } from "next-intl";
import { Badge } from "@country-decision-atlas/ui";
import type { AIAskResponse } from "../../shared/api/ai";
import { AICitationsList } from "./AICitationsList";
import { AIDisclaimer } from "./AIDisclaimer";
import { AIRefusalState } from "./AIRefusalState";

type AIAnswerCardProps = {
  response: AIAskResponse;
};

export function AIAnswerCard({ response }: AIAnswerCardProps) {
  const t = useTranslations("aiAnswerCard");
  const citationCount = response.citations?.length ?? 0;
  const isUncited = !response.refused && citationCount === 0;

  return (
    <article
      className="flex flex-col gap-4"
      data-testid="ai-answer-card"
    >
      {response.refused ? (
        <AIRefusalState message={response.answer} />
      ) : isUncited ? (
        <div
          className="border-warm flex flex-col gap-2 border px-4 py-3"
          data-testid="ai-answer-uncited"
        >
          <Badge variant="warning">{t("uncitedBadge")}</Badge>
          <p className="text-c3 text-sm leading-relaxed">{response.answer}</p>
          <p className="text-c4 text-xs">{t("uncitedWarning")}</p>
        </div>
      ) : (
        <p className="text-c1 text-sm leading-relaxed">{response.answer}</p>
      )}
      <AICitationsList citations={response.citations} />
      <AIDisclaimer text={response.disclaimer} />
      <p
        className="text-c4 font-mono text-[9px] tracking-[0.05em] uppercase"
        data-testid="ai-provider-meta"
      >
        {t("providerMeta", {
          provider: response.provider,
          mode: response.mode,
          count: response.context_items_count,
        })}
      </p>
    </article>
  );
}
