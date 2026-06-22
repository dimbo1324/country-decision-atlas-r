import type { ComparedMetric, ComparedCountry } from "../../shared/api/cii";

type Props = {
  metrics: ComparedMetric[];
  countries: ComparedCountry[];
  size?: number;
};

const COUNTRY_COLORS = ["#1a6abf", "#b85c00"];
const COUNTRY_FILL_OPACITY = 0.15;

function polarToXY(
  cx: number,
  cy: number,
  r: number,
  angleRad: number,
): [number, number] {
  return [cx + r * Math.sin(angleRad), cy - r * Math.cos(angleRad)];
}

function buildPolygon(
  cx: number,
  cy: number,
  radius: number,
  values: number[],
  angles: number[],
): string {
  return values
    .map((v, i) => {
      const r = (v / 100) * radius;
      const [x, y] = polarToXY(cx, cy, r, angles[i]!);
      return `${x},${y}`;
    })
    .join(" ");
}

export function CiiCompareSpiderChart({ metrics, countries, size = 280 }: Props) {
  if (metrics.length === 0) return null;

  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.38;
  const n = metrics.length;
  const angles = Array.from({ length: n }, (_, i) => (2 * Math.PI * i) / n);

  const countryValues: number[][] = countries.map((_, ci) =>
    metrics.map((m) => {
      const v = (m.values ?? []).find((mv) => mv.country_slug === countries[ci]?.slug);
      return v?.effective_value ?? 0;
    }),
  );

  const gridLevels = [20, 40, 60, 80, 100];

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width={size}
      height={size}
      className="ciiSpiderChart"
      aria-label="CII spider chart"
    >
      {gridLevels.map((level) => {
        const pts = angles
          .map((a) => {
            const r = (level / 100) * radius;
            const [x, y] = polarToXY(cx, cy, r, a);
            return `${x},${y}`;
          })
          .join(" ");
        return (
          <polygon
            key={level}
            points={pts}
            fill="none"
            stroke="currentColor"
            strokeOpacity="0.15"
            strokeWidth="1"
          />
        );
      })}

      {angles.map((angle, i) => {
        const [x, y] = polarToXY(cx, cy, radius, angle);
        return (
          <line
            key={i}
            x1={cx}
            y1={cy}
            x2={x}
            y2={y}
            stroke="currentColor"
            strokeOpacity="0.15"
            strokeWidth="1"
          />
        );
      })}

      {countryValues.map((vals, ci) => (
        <polygon
          key={countries[ci]?.slug ?? ci}
          points={buildPolygon(cx, cy, radius, vals, angles)}
          fill={COUNTRY_COLORS[ci] ?? "#888"}
          fillOpacity={COUNTRY_FILL_OPACITY}
          stroke={COUNTRY_COLORS[ci] ?? "#888"}
          strokeWidth="1.5"
        />
      ))}

      {angles.map((angle, i) => {
        const labelR = radius + 20;
        const [x, y] = polarToXY(cx, cy, labelR, angle);
        const anchor = Math.abs(x - cx) < 4 ? "middle" : x < cx ? "end" : "start";
        const label = metrics[i]?.metric_name ?? "";
        const words = label.split(" ");
        return (
          <text
            key={i}
            x={x}
            y={y}
            textAnchor={anchor}
            dominantBaseline="middle"
            fontSize="9"
            fill="currentColor"
          >
            {words.length <= 2 ? (
              label
            ) : (
              <>
                <tspan x={x} dy="-6">
                  {words.slice(0, Math.ceil(words.length / 2)).join(" ")}
                </tspan>
                <tspan x={x} dy="11">
                  {words.slice(Math.ceil(words.length / 2)).join(" ")}
                </tspan>
              </>
            )}
          </text>
        );
      })}
    </svg>
  );
}
