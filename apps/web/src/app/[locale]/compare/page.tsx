import { getLocale } from "next-intl/server";
import { CompareMatrixView } from "../../../features/compare-matrix/CompareMatrixView";

export const dynamic = "force-dynamic";

export default async function ComparePage() {
  const locale = await getLocale();
  return (
    <main className="pageShell">
      <header className="pageHeader">
        <p className="eyebrow">Сравнение</p>
        <h1>Сравнение стран по сценариям</h1>
        <p className="pageSubtitle">
          Матрица показывает CII-оценку по каждому сценарию для каждой страны.
        </p>
      </header>
      <CompareMatrixView locale={locale} />
    </main>
  );
}
