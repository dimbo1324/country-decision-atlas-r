export const CII_AXES = [
  "Стабильность",
  "Верховенство закона",
  "Эконом. свобода",
  "Стоимость жизни",
  "ВНЖ",
  "Качество жизни",
  "Цифра",
  "Drift",
];

export const CII_COUNTRIES = {
  a: { name: "Сингапур", values: [88, 91, 94, 52, 61, 89, 96, 74] },
  b: { name: "Португалия", values: [79, 74, 68, 71, 83, 82, 70, 66] },
};

export const LEGAL_VELOCITY_TIMELINE = [
  4.1, 4.6, 5.0, 4.8, 5.4, 5.9, 5.6, 6.1, 6.6, 6.2, 6.8, 7.1, 6.9, 7.4, 7.0,
  6.7, 7.2, 7.6, 7.3, 7.8, 8.1, 7.7, 8.3, 8.6,
];

export const COUNTRY_DRIFT_TIMELINE = [
  -1.2, -0.6, 0.1, 0.8, 1.4, 1.1, 2.0, 2.6, 3.1, 2.8, 3.6, 4.2, 3.9, 4.8, 5.3,
  5.0, 5.8, 6.2, 5.9, 6.6, 7.0, 6.8, 7.2, 7.2,
];

export const SCENARIO_MATRIX = {
  scenarios: ["Релокация", "Резидентство", "Бизнес", "Низкий бюджет"],
  countries: [
    "Сингапур",
    "Португалия",
    "Уругвай",
    "Аргентина",
    "Россия",
    "ОАЭ",
  ],
  values: [
    [81, 74, 62, 58, 41, 88],
    [58, 89, 55, 61, 44, 77],
    [92, 68, 71, 47, 39, 90],
    [39, 65, 58, 79, 60, 45],
  ],
};

export interface TrustDimension {
  label: string;
  value: number;
  detail: string;
}

export const TRUST_DIMENSIONS: TrustDimension[] = [
  {
    label: "Источники",
    value: 94,
    detail: "OECD, World Bank, национальные реестры",
  },
  { label: "Свежесть", value: 88, detail: "Медиана верификации — 34 дня" },
  {
    label: "Методология",
    value: 96,
    detail: "Версионируется, изменения аудируются",
  },
  {
    label: "Прозрачность",
    value: 91,
    detail: "Разбивка confidence по каждой метрике",
  },
];

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

export const CATALOG_COUNTRIES: CatalogCountry[] = [
  {
    slug: "singapore",
    name: "Сингапур",
    flag: "SG",
    ciiScore: 91,
    confidence: 0.96,
    driftLabel: "Открывается",
    driftValue: 7.2,
    summary:
      "Высочайшая экономическая свобода и цифровая инфраструктура; стоимость жизни — главный барьер входа.",
    tags: ["business", "digital", "high-cost"],
  },
  {
    slug: "portugal",
    name: "Португалия",
    flag: "PT",
    ciiScore: 79,
    confidence: 0.91,
    driftLabel: "Стабильно",
    driftValue: 1.4,
    summary:
      "Развитая программа резидентства для не-ЕС граждан, умеренная стоимость жизни, солидное качество жизни.",
    tags: ["residency", "quality-of-life"],
  },
  {
    slug: "uruguay",
    name: "Уругвай",
    flag: "UY",
    ciiScore: 71,
    confidence: 0.84,
    driftLabel: "Открывается",
    driftValue: 4.8,
    summary:
      "Предсказуемая правовая система и низкая политическая турбулентность — тихая гавань для релокации.",
    tags: ["safety", "residency"],
  },
  {
    slug: "argentina",
    name: "Аргентина",
    flag: "AR",
    ciiScore: 58,
    confidence: 0.77,
    driftLabel: "Турбулентно",
    driftValue: -3.1,
    summary:
      "Низкая стоимость жизни компенсирует макроэкономическую нестабильность; высокая частота изменений закона.",
    tags: ["low-budget"],
  },
];
