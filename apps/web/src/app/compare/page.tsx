import { CompareMatrixView } from "../../features/compare-matrix/CompareMatrixView";

export const dynamic = "force-dynamic";

export default function ComparePage() {
  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Сравнение</p>
        <h1>Сравнение стран по сценариям</h1>
        <p className="pageSubtitle">
          Матрица показывает CII-оценку по каждому сценарию для каждой страны.
        </p>
      </header>
      <CompareMatrixView locale="ru" />
    </main>
  );
}
