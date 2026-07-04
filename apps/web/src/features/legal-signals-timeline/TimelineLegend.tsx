const directions = [
  ["positive", "Положительное"],
  ["negative", "Негативное"],
  ["neutral", "Нейтральное"],
  ["mixed", "Смешанное"],
  ["uncertain", "Неопределённое"],
] as const;

export function TimelineLegend() {
  return (
    <div
      className="timelineLegend"
      data-testid="legal-signals-timeline-legend"
    >
      <strong>Направление влияния</strong>
      {directions.map(([value, label]) => (
        <span
          key={value}
          className={`timelineLegendItem timelineEvent${capitalize(value)}`}
        >
          {label}
        </span>
      ))}
    </div>
  );
}

function capitalize(value: string) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}
