"use client";

import { DecisionRunForm } from "../../features/decision-run";

export default function DecisionPage() {
  return (
    <div className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Decision</p>
        <h1>Decision engine</h1>
      </header>
      <DecisionRunForm />
    </div>
  );
}
