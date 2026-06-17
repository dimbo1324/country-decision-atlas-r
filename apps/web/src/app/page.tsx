const signals = ["Immigration", "Cost", "Safety", "Healthcare", "Work", "Tax"];
export default function Home() {
  return (
    <main className="shell">
      <section className="intro">
        <p className="eyebrow">Country Decision Atlas</p>
        <h1>Relocation decisions with sourced country intelligence.</h1>
        <p>
          This placeholder keeps the web app runnable while the product model,
          data contracts, and scoring workflows are built out.
        </p>
      </section>
      <section className="signalGrid" aria-label="Decision signals">
        {signals.map((signal) => (
          <article key={signal}>
            <span>{signal}</span>
          </article>
        ))}
      </section>
    </main>
  );
}
