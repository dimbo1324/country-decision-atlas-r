export const CII_AXES = [
  "Стабильность",
  "Верховенство закона",
  "Эконом. свобода",
  "Стоимость жизни",
  "ВНЖ",
  "Качество жизни",
  "Цифра",
  "Дрейф",
];

export const SCENARIOS = [
  "Релокация",
  "Резидентство",
  "Бизнес",
  "Низкий бюджет",
];

interface FictionalCountryProfile {
  id: string;
  name: string;
  flag: string;
  summary: string;
  tags: string[];
}

export const FICTIONAL_COUNTRIES: FictionalCountryProfile[] = [
  {
    id: "aurelia",
    name: "Аврелия",
    flag: "AVR",
    summary:
      "Высокая экономическая свобода и развитая цифровая инфраструктура; стоимость жизни — главный барьер входа.",
    tags: ["бизнес", "цифровая инфраструктура", "дорого"],
  },
  {
    id: "karindor",
    name: "Кариндор",
    flag: "KDR",
    summary:
      "Устойчивая программа резидентства и умеренная стоимость жизни; качество жизни выше среднего.",
    tags: ["резидентство", "качество жизни"],
  },
  {
    id: "vesmaria",
    name: "Весмария",
    flag: "VSM",
    summary:
      "Низкая стоимость жизни компенсирует политическую турбулентность; высокая частота изменений законодательства.",
    tags: ["низкий бюджет", "нестабильность"],
  },
];

export interface CiiSeries {
  id: string;
  name: string;
  values: number[];
}

export interface CatalogCountry {
  slug: string;
  name: string;
  flag: string;
  ciiScore: number;
  confidence: number;
  driftLabel: string;
  driftValue: number;
  summary: string;
  tags: string[];
}

export interface TrustDimension {
  label: string;
  value: number;
  detail: string;
}

export interface Dataset {
  version: number;
  ciiSeries: CiiSeries[];
  legalVelocityTimeline: number[];
  countryDriftTimeline: number[];
  scenarioLeftName: string;
  scenarioRightName: string;
  scenarioLeftValues: number[];
  scenarioRightValues: number[];
  trustDimensions: TrustDimension[];
  catalog: CatalogCountry[];
}

function randomInRange(min: number, max: number): number {
  return min + Math.random() * (max - min);
}

function randomWalk(
  length: number,
  start: number,
  drift: number,
  noise: number,
): number[] {
  const series: number[] = [];
  let current = start;
  for (let i = 0; i < length; i += 1) {
    current += drift + (Math.random() - 0.5) * noise;
    series.push(Math.round(current * 10) / 10);
  }
  return series;
}

function driftLabelFor(value: number): string {
  if (value > 1.5) return "Открывается";
  if (value < -1.5) return "Турбулентно";
  return "Стабильно";
}

let versionCounter = 0;

export function generateDataset(): Dataset {
  versionCounter += 1;

  const ciiSeries: CiiSeries[] = FICTIONAL_COUNTRIES.map((country) => ({
    id: country.id,
    name: country.name,
    values: CII_AXES.map(() => Math.round(randomInRange(38, 96))),
  }));

  const catalog: CatalogCountry[] = FICTIONAL_COUNTRIES.map(
    (country, index) => {
      const axisValues = ciiSeries[index].values;
      const ciiScore = Math.round(
        axisValues.reduce((sum, value) => sum + value, 0) / axisValues.length,
      );
      const driftValue = Math.round(randomInRange(-8, 8) * 10) / 10;
      return {
        slug: country.id,
        name: country.name,
        flag: country.flag,
        ciiScore,
        confidence: Math.round(randomInRange(0.72, 0.98) * 100) / 100,
        driftLabel: driftLabelFor(driftValue),
        driftValue,
        summary: country.summary,
        tags: country.tags,
      };
    },
  );

  const trustDimensions: TrustDimension[] = [
    {
      label: "Источники",
      value: Math.round(randomInRange(88, 97)),
      detail: "ОЭСР, Всемирный банк, национальные реестры",
    },
    {
      label: "Свежесть",
      value: Math.round(randomInRange(80, 94)),
      detail: `Медиана верификации — ${Math.round(randomInRange(20, 45))} дней`,
    },
    {
      label: "Методология",
      value: Math.round(randomInRange(90, 99)),
      detail: "Версионируется, изменения аудируются",
    },
    {
      label: "Прозрачность",
      value: Math.round(randomInRange(85, 96)),
      detail: "Разбивка достоверности по каждой метрике",
    },
  ];

  return {
    version: versionCounter,
    ciiSeries,
    legalVelocityTimeline: randomWalk(24, randomInRange(3, 5), 0.14, 0.9),
    countryDriftTimeline: randomWalk(24, randomInRange(-2, 2), 0.32, 1.1),
    scenarioLeftName: FICTIONAL_COUNTRIES[0].name,
    scenarioRightName: FICTIONAL_COUNTRIES[2].name,
    scenarioLeftValues: SCENARIOS.map(() => Math.round(randomInRange(35, 92))),
    scenarioRightValues: SCENARIOS.map(() => Math.round(randomInRange(35, 92))),
    trustDimensions,
    catalog,
  };
}
