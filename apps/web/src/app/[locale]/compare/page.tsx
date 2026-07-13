import { getLocale } from "next-intl/server";
import { Kicker } from "@country-decision-atlas/ui";
import { CompareMatrixView } from "../../../features/compare-matrix/CompareMatrixView";

export default async function ComparePage() {
  const locale = await getLocale();
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Сравнение</Kicker>
        <h1 className="font-display text-3xl font-bold">
          Сравнение стран по сценариям
        </h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Матрица показывает CII-оценку по каждому сценарию для каждой страны.
        </p>
      </header>
      <CompareMatrixView locale={locale} />
    </div>
  );
}
