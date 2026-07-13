import { Kicker } from "@country-decision-atlas/ui";
import { GlossaryView } from "../../../features/glossary";

export const dynamic = "force-dynamic";

export default function GlossaryPage() {
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3">
        <Kicker>Глоссарий</Kicker>
        <h1 className="font-display text-4xl font-bold">
          Глоссарий терминов платформы
        </h1>
        <p className="text-c3 max-w-2xl text-sm leading-relaxed">
          Определения ключевых терминов, используемых в оценках, скорах и
          отчётах платформы.
        </p>
      </header>
      <GlossaryView />
    </div>
  );
}
