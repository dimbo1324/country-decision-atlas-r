const BANDS = [
  { label: "weak", text: "Слабый (0–30)", className: "matrixCellWeak" },
  { label: "limited", text: "Ограниченный (30–50)", className: "matrixCellLimited" },
  { label: "moderate", text: "Средний (50–70)", className: "matrixCellModerate" },
  { label: "strong", text: "Сильный (70–85)", className: "matrixCellStrong" },
  { label: "excellent", text: "Отличный (85–100)", className: "matrixCellExcellent" },
];

export function MatrixLegend() {
  return (
    <div className="matrixLegend" data-testid="compare-matrix-legend">
      <h3 className="matrixLegendTitle">Легенда</h3>
      <div className="matrixLegendBands">
        {BANDS.map((b) => (
          <div key={b.label} className="matrixLegendItem">
            <span className={`matrixLegendDot ${b.className}`} />
            <span>{b.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
