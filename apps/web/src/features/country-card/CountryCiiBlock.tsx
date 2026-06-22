import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { ConfidenceBadge } from "../../shared/ui/ConfidenceBadge";

type CiiData = NonNullable<CountryReadModelResponse["cii"]>;
type CiiMetric = CiiData["metrics"][number];

type CountryCiiBlockProps = {
  cii: CiiData | null | undefined;
};

const METRIC_LABEL_RU: Record<string, string> = {
  rule_of_law: "Верховенство права",
  economic_freedom: "Экон. свобода",
  political_stability: "Пол. стабильность",
  safety: "Безопасность",
  corruption: "Антикоррупция",
  digital_access: "Цифровой доступ",
};

const SCORE_TIERS = [
  { min: 75, label: "Высокий", cls: "ciiTierHigh" },
  { min: 50, label: "Средний", cls: "ciiTierMid" },
  { min: 25, label: "Ниже среднего", cls: "ciiTierLow" },
  { min: 0, label: "Низкий", cls: "ciiTierVeryLow" },
];

function scoreTier(score: number) {
  return SCORE_TIERS.find((t) => score >= t.min) ?? SCORE_TIERS[SCORE_TIERS.length - 1];
}

function SpiderChart({ metrics }: { metrics: CiiMetric[] }) {
  if (metrics.length === 0) return null;

  const N = metrics.length;
  const cx = 150;
  const cy = 150;
  const R = 120;
  const levels = [25, 50, 75, 100];

  function polar(angleDeg: number, r: number) {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  const angleStep = 360 / N;
  const axes = metrics.map((m, i) => ({
    angle: i * angleStep,
    label: METRIC_LABEL_RU[m.slug] ?? m.name_en,
    score: m.score,
  }));

  const gridPolygons = levels.map((lvl) => {
    const pts = axes.map((a) => {
      const p = polar(a.angle, (R * lvl) / 100);
      return `${p.x},${p.y}`;
    });
    return pts.join(" ");
  });

  const dataPoints = axes.map((a) => {
    const p = polar(a.angle, (R * Math.min(a.score, 100)) / 100);
    return `${p.x},${p.y}`;
  });

  return (
    <svg
      viewBox="0 0 300 300"
      width="260"
      height="260"
      aria-label="CII spider chart"
      role="img"
      className="ciiSpider"
    >
      {gridPolygons.map((pts, i) => (
        <polygon
          key={i}
          points={pts}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth="1"
          opacity={0.5 + i * 0.1}
        />
      ))}

      {axes.map((a) => {
        const end = polar(a.angle, R);
        return (
          <line
            key={a.label}
            x1={cx}
            y1={cy}
            x2={end.x}
            y2={end.y}
            stroke="var(--color-border)"
            strokeWidth="1"
            opacity={0.6}
          />
        );
      })}

      <polygon
        points={dataPoints.join(" ")}
        fill="var(--color-accent, #3b82f6)"
        fillOpacity={0.2}
        stroke="var(--color-accent, #3b82f6)"
        strokeWidth="2"
      />

      {axes.map((a) => {
        const p = polar(a.angle, (R * Math.min(a.score, 100)) / 100);
        return (
          <circle
            key={a.label}
            cx={p.x}
            cy={p.y}
            r={4}
            fill="var(--color-accent, #3b82f6)"
          />
        );
      })}

      {axes.map((a) => {
        const labelR = R + 20;
        const p = polar(a.angle, labelR);
        const anchor = Math.abs(p.x - cx) < 5 ? "middle" : p.x < cx ? "end" : "start";
        return (
          <text
            key={a.label}
            x={p.x}
            y={p.y}
            textAnchor={anchor}
            dominantBaseline="middle"
            fontSize="9"
            fill="var(--color-text-secondary, #6b7280)"
          >
            {a.label}
          </text>
        );
      })}
    </svg>
  );
}

export function CountryCiiBlock({ cii }: CountryCiiBlockProps) {
  if (!cii) {
    return <EmptyState message="CII-данные для этой страны ещё не рассчитаны." />;
  }

  const tier = scoreTier(cii.overall_score);

  return (
    <div className="ciiBlock" data-testid="cii-block">
      <div className="ciiScoreRow">
        <div className="ciiScorePrimary">
          <span className={`ciiScoreValue ${tier.cls}`}>
            {Math.round(cii.overall_score)}
          </span>
          <span className="ciiScoreMax">/100</span>
          <span className={`ciiTierBadge ${tier.cls}`}>{tier.label}</span>
        </div>
        <div className="ciiMeta">
          <ConfidenceBadge confidence={cii.confidence} />
          {cii.drift !== null && cii.drift !== undefined ? (
            <span className="ciiDriftBadge">
              Динамика: {cii.drift > 0 ? "+" : ""}
              {cii.drift.toFixed(1)}
            </span>
          ) : (
            <span className="ciiDriftBadge ciiDriftNa">Динамика: н/д</span>
          )}
          <span className="ciiVersion">Версия {cii.version}</span>
          {cii.aggregation_method && (
            <span className="ciiMethodBadge">{cii.aggregation_method}</span>
          )}
        </div>
      </div>

      <div className="ciiChartRow">
        <SpiderChart metrics={cii.metrics} />

        {cii.metrics.length > 0 && (
          <div className="ciiMetricList">
            {cii.metrics.map((m) => {
              const mTier = scoreTier(m.score);
              return (
                <div key={m.slug} className="ciiMetricRow">
                  <span className="ciiMetricName">
                    {METRIC_LABEL_RU[m.slug] ?? m.name_en}
                  </span>
                  <span className="ciiMetricBar">
                    <span
                      className={`ciiMetricFill ${mTier.cls}`}
                      style={{ width: `${Math.round(m.score)}%` }}
                    />
                  </span>
                  <span className={`ciiMetricScore ${mTier.cls}`}>
                    {Math.round(m.score)}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <p className="ciiDisclaimer">
        CII — составной индекс: верховенство права, экон. свобода, полит. стабильность,
        безопасность, антикоррупция, цифровой доступ. Выше = лучше.
      </p>
    </div>
  );
}
