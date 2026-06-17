import { apiGet } from "../lib/api";

export const dynamic = "force-dynamic";

type LegalSignals = {
  items: Array<{
    id: string;
    title: string;
    signal_type: string;
    impact_direction: string;
    impact_level: string;
  }>;
};

export default async function LegalSignalsPage() {
  const signals = await apiGet<LegalSignals>("/api/v1/legal-signals?locale=en");

  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Legal signals</p>
        <h1>Traceable decision signals</h1>
      </header>

      {signals.ok ? (
        <section className="dataGrid">
          {signals.data.items.map((signal) => (
            <article className="dataCard" key={signal.id}>
              <span>{signal.title}</span>
              <small>
                {signal.signal_type} / {signal.impact_direction} / {signal.impact_level}
              </small>
            </article>
          ))}
        </section>
      ) : (
        <p className="notice">{signals.error}</p>
      )}
    </main>
  );
}
