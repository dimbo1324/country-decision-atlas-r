import { CompareMatrixView } from "../../features/compare-matrix/CompareMatrixView";
import { getLocaleFromSearchParams } from "../../shared/lib/locale";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ComparePage({ searchParams }: PageProps) {
  const locale = getLocaleFromSearchParams(await searchParams);
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
