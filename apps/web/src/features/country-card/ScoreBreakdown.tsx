import type { CountryReadModelResponse } from "../../shared/api/countries";

type ScoreBreakdownItem = NonNullable<
  CountryReadModelResponse["scores"][number]["breakdowns"]
>[number];

type CountryReadModelSource = CountryReadModelResponse["sources"][number];

type ScoreBreakdownProps = {
  breakdowns: ScoreBreakdownItem[];
  sourcesById?: Map<string, CountryReadModelSource>;
};

export function ScoreBreakdown({ breakdowns, sourcesById }: ScoreBreakdownProps) {
  const linkedSources: CountryReadModelSource[] = [];
  if (sourcesById) {
    const seen = new Set<string>();
    for (const b of breakdowns) {
      for (const sid of b.source_ids ?? []) {
        if (!seen.has(sid)) {
          seen.add(sid);
          const s = sourcesById.get(sid);
          if (s) linkedSources.push(s);
        }
      }
    }
  }

  return (
    <div className="breakdownBlock">
      <div className="breakdownWrap">
        <table className="breakdownTable">
          <thead>
            <tr>
              <th>Критерий</th>
              <th>Оценка</th>
              <th>Вес</th>
              <th>Взвешенная</th>
              <th>Достоверность</th>
            </tr>
          </thead>
          <tbody>
            {breakdowns.map((b) => (
              <tr key={b.criterion}>
                <td>{b.criterion}</td>
                <td>{b.score}</td>
                <td>{b.weight}</td>
                <td>{b.weighted_score}</td>
                <td>{b.confidence ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {linkedSources.length > 0 && (
        <div className="supportingSourcesList" data-testid="supporting-sources">
          <p className="sectionTitle">Подтверждающие источники</p>
          {linkedSources.map((s) => (
            <div key={s.id} className="sourceLinkCard">
              <span className="sourceLinkTitle">{s.title}</span>
              <div className="metaRow">
                {s.source_type && <span className="metaChip">{s.source_type}</span>}
                {s.confidence && (
                  <span className="metaChip">Достоверность: {s.confidence}</span>
                )}
              </div>
              <a href={s.url} target="_blank" rel="noreferrer" className="externalLink">
                Открыть источник ↗
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
