"use client";

import { DecisionRunForm } from "../../../features/decision-run";

export default function DecisionPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Движок подбора</p>
        <h1>Запустить подбор страны</h1>
        <p className="pageSubtitle">
          Выберите страну отправления, страны-кандидаты и сценарий. Движок
          вернёт ранжированный объяснимый результат с оценками, сильными
          сторонами, слабыми сторонами, рисками и разбором оценки с источниками.
        </p>
      </header>
      <DecisionRunForm />
    </div>
  );
}
