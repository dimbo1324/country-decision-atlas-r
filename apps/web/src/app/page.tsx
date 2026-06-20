import Link from "next/link";
import { routes } from "../shared/lib/routes";

const ANALYSIS_ITEMS = [
  "Резидентство и миграция",
  "Долгосрочный статус и гражданство",
  "Стоимость жизни",
  "Бизнес и самозанятость",
  "Безопасность и политические риски",
  "Источники и доказательства",
];

export default function Home() {
  return (
    <div className="homePage">
      <section className="homeHero">
        <p className="eyebrow">Country Decision Atlas</p>
        <h1>Сравнивайте страны с источниками и доказательствами.</h1>
        <p className="heroSubtitle">
          Country Decision Atlas помогает сравнивать страны с помощью структурированных
          карточек, правовых сигналов, сценарных оценок и объяснимых результатов
          подбора.
        </p>
        <div className="homeActions">
          <Link href={routes.countries} className="homeActionPrimary">
            Смотреть страны
          </Link>
          <Link href={routes.decision} className="homeActionSecondary">
            Запустить подбор
          </Link>
        </div>
      </section>

      <section className="homeSection">
        <h2 className="homeSectionTitle">MVP: Россия vs Уругвай</h2>
        <p className="homeSectionDesc">
          Текущий MVP сравнивает две страны по сценариям переезда, резидентства,
          бизнеса, безопасности и долгосрочной миграции.
        </p>
        <div className="homeCountryCards">
          <div className="homeCountryCard">
            <span className="homeCountryName">Россия</span>
            <span className="homeCountryIso">RU</span>
            <div className="homeCountryLinks">
              <Link href={`${routes.country("russia")}`} className="homeCountryLink">
                Карточка страны
              </Link>
              <Link
                href={`${routes.decision}?origin=russia`}
                className="homeCountryLink"
              >
                Запустить подбор
              </Link>
            </div>
          </div>
          <div className="homeCountryCard">
            <span className="homeCountryName">Уругвай</span>
            <span className="homeCountryIso">UY</span>
            <div className="homeCountryLinks">
              <Link href={`${routes.country("uruguay")}`} className="homeCountryLink">
                Карточка страны
              </Link>
              <Link
                href={`${routes.decision}?origin=uruguay`}
                className="homeCountryLink"
              >
                Запустить подбор
              </Link>
            </div>
          </div>
        </div>
        <Link href={routes.decision} className="homeCompareLink">
          Сравнение Россия vs Уругвай →
        </Link>
      </section>

      <section className="homeSection">
        <h2 className="homeSectionTitle">Что анализирует платформа</h2>
        <ul className="homeAnalysisList">
          {ANALYSIS_ITEMS.map((item) => (
            <li key={item} className="homeAnalysisItem">
              {item}
            </li>
          ))}
        </ul>
      </section>

      <section className="homeSection homeTrustSection">
        <h2 className="homeSectionTitle">Решения на основе источников</h2>
        <p className="homeSectionDesc">
          Оценки не показываются в одиночку. Каждая оценка связана с разбором критериев,
          правовыми сигналами, документами-источниками и доказательствами — чтобы было
          видно, почему страна занимает то или иное место.
        </p>
        <div className="homeTrustLinks">
          <Link href={routes.legalSignals} className="homeTrustLink">
            Правовые сигналы →
          </Link>
          <Link href={routes.sources} className="homeTrustLink">
            Источники →
          </Link>
        </div>
      </section>
    </div>
  );
}
