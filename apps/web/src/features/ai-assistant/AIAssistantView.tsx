"use client";

import { useState } from "react";
import type { AIAskResponse } from "../../shared/api/ai";
import type { SupportedLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { AIAnswerCard } from "./AIAnswerCard";
import { AIAskForm } from "./AIAskForm";

type AIAssistantViewProps = {
  locale: SupportedLocale;
};

export function AIAssistantView({ locale }: AIAssistantViewProps) {
  const [response, setResponse] = useState<AIAskResponse | null>(null);

  return (
    <div
      className="decisionLayout"
      data-testid="ai-assistant-page"
    >
      <AIAskForm
        locale={locale}
        onResponse={setResponse}
      />
      <div>
        {response ? (
          <AIAnswerCard response={response} />
        ) : (
          <EmptyState message="Задайте вопрос по опубликованным данным проекта." />
        )}
      </div>
    </div>
  );
}
