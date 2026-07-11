import { SlideSection } from "@/components/shell/SlideSection";
import { Kicker } from "@/components/ui/Kicker";
import { PassportCard } from "@/components/ui/PassportCard";
import { Accordion } from "@/components/ui/Accordion";
import type { Dataset } from "@/data/generator";

interface PassportSlideProps {
  active: boolean;
  dataset: Dataset;
}

export function PassportSlide({ active, dataset }: PassportSlideProps) {
  return (
    <SlideSection className="grid grid-cols-1 items-center gap-12 lg:grid-cols-[0.85fr_1fr]">
      <div className="flex flex-col gap-6">
        <Kicker>Origin-Aware Decision</Kicker>
        <h2 className="font-display text-4xl leading-tight font-bold sm:text-5xl">
          Решение как
          <br />
          <em className="text-gold3 not-italic">осязаемый документ</em>
        </h2>
        <p className="text-c2 max-w-md text-base leading-relaxed">
          Паспорт решения — экспортируемый source-backed отчёт по паре «откуда →
          куда» с учётом трансграничной совместимости: виза, налоговое
          соглашение, банки, часовой пояс. Тумблеры пересчитывают скор вживую.
        </p>
        <Accordion
          items={[
            {
              title: "Как считается скор CBLC",
              meta: "Методология",
              content:
                "Базовый скор совместимости пары юрисдикций плюс явные бонусы за налоговое соглашение и сценарий. Каждое слагаемое видно отдельно — никаких скрытых поправок.",
            },
            {
              title: "Откуда данные",
              meta: "Источники",
              content:
                "Каждая ячейка паспорта подкреплена источником с датой верификации. Прозрачность источника важнее лаконичности.",
            },
            {
              title: "Что не входит в скор",
              meta: "Границы",
              content:
                "Репутация, донаты и любые платные атрибуты никогда не влияют на скор — деньги не покупают позицию в рейтинге.",
            },
          ]}
        />
      </div>

      <PassportCard
        key={dataset.version}
        passport={dataset.passport}
        active={active}
      />
    </SlideSection>
  );
}
