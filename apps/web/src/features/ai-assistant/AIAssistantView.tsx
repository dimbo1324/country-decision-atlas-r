"use client";

import { useState } from "react";
import { Card, Kicker, useReducedMotion } from "@country-decision-atlas/ui";
import type { AIAskResponse } from "../../shared/api/ai";
import type { SupportedLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { AIAnswerCard } from "./AIAnswerCard";
import { AIAskForm } from "./AIAskForm";

type AIAssistantViewProps = {
  locale: SupportedLocale;
};

function TypingIndicator() {
  const reducedMotion = useReducedMotion();

  if (reducedMotion) {
    return (
      <p
        className="text-c3 text-sm"
        data-testid="ai-typing-indicator"
      >
        Готовим ответ…
      </p>
    );
  }

  return (
    <div
      className="flex items-center gap-1.5"
      data-testid="ai-typing-indicator"
      aria-label="Готовим ответ…"
    >
      {[0, 1, 2].map((index) => (
        <span
          key={index}
          className="bg-gold h-1.5 w-1.5 animate-bounce rounded-full"
          style={{ animationDelay: `${index * 120}ms` }}
        />
      ))}
    </div>
  );
}

export function AIAssistantView({ locale }: AIAssistantViewProps) {
  const [response, setResponse] = useState<AIAskResponse | null>(null);
  const [isAsking, setIsAsking] = useState(false);

  return (
    <div
      className="grid grid-cols-1 gap-6 lg:grid-cols-2"
      data-testid="ai-assistant-page"
    >
      <Card
        interactive={false}
        className="flex flex-col gap-4"
      >
        <Kicker>Задать вопрос</Kicker>
        <AIAskForm
          locale={locale}
          onResponse={(next) => {
            setIsAsking(false);
            setResponse(next);
          }}
          onPendingChange={setIsAsking}
        />
      </Card>
      <div className="flex flex-col gap-4">
        {isAsking && !response ? (
          <TypingIndicator />
        ) : response ? (
          <AIAnswerCard response={response} />
        ) : (
          <EmptyState message="Задайте вопрос по опубликованным данным проекта." />
        )}
      </div>
    </div>
  );
}
