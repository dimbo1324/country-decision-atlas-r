import type { AIAskResponse } from "../../shared/api/ai";
import { AICitationsList } from "./AICitationsList";
import { AIDisclaimer } from "./AIDisclaimer";
import { AIRefusalState } from "./AIRefusalState";

type AIAnswerCardProps = {
  response: AIAskResponse;
};

export function AIAnswerCard({ response }: AIAnswerCardProps) {
  return (
    <article
      className="resultCard"
      data-testid="ai-answer-card"
    >
      {response.refused ? (
        <AIRefusalState message={response.answer} />
      ) : (
        <p className="resultSummary">{response.answer}</p>
      )}
      <AICitationsList citations={response.citations} />
      <AIDisclaimer text={response.disclaimer} />
      <p
        className="formHint"
        data-testid="ai-provider-meta"
      >
        Provider: {response.provider} · mode: {response.mode} · context:{" "}
        {response.context_items_count}
      </p>
    </article>
  );
}
