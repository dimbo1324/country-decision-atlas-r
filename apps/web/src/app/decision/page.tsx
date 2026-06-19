"use client";

import { DecisionRunForm } from "../../features/decision-run";

export default function DecisionPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Decision engine</p>
        <h1>Run a country decision</h1>
        <p className="pageSubtitle">
          Choose an origin country, select candidates, and pick a scenario.
          The engine returns a ranked, explainable result with scores, strengths,
          weaknesses, risk warnings, and source-backed breakdown.
        </p>
      </header>
      <DecisionRunForm />
    </div>
  );
}
