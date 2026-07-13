"use client";

import { Kicker } from "@country-decision-atlas/ui";
import { DecisionRunForm } from "../../../features/decision-run";

export default function DecisionPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Движок подбора</Kicker>
        <h1 className="font-display text-3xl font-bold">
          Запустить подбор страны
        </h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Выберите страну отправления, страны-кандидаты и сценарий. Движок
          вернёт ранжированный объяснимый результат с оценками, сильными
          сторонами, слабыми сторонами, рисками и разбором оценки с источниками.
        </p>
      </header>
      <DecisionRunForm />
    </div>
  );
}
