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

export const HEATMAP_MONTHS = [
  "Янв",
  "Фев",
  "Мар",
  "Апр",
  "Май",
  "Июн",
  "Июл",
  "Авг",
  "Сен",
  "Окт",
  "Ноя",
  "Дек",
];

export const RANK_QUARTERS = [
  "К1'25",
  "К2'25",
  "К3'25",
  "К4'25",
  "К1'26",
  "К2'26",
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
  {
    id: "norvintia",
    name: "Норвинтия",
    flag: "NRV",
    summary:
      "Северная юрисдикция с образцовыми институтами и предсказуемым правом; высокие налоги и закрытый рынок труда.",
    tags: ["стабильность", "институты", "дорого"],
  },
  {
    id: "estarra",
    name: "Эстарра",
    flag: "EST",
    summary:
      "Островной налоговый режим для удалённых специалистов; слабая цифровая инфраструктура за пределами столицы.",
    tags: ["низкие налоги", "удалённая работа"],
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

export interface DriftBoardRow {
  slug: string;
  name: string;
  flag: string;
  timeline: number[];
  driftValue: number;
  statusLabel: string;
  status: "pos" | "mild" | "stable" | "neg";
}

export interface HeatmapData {
  rows: string[];
  columns: string[];
  values: number[][];
}

export interface RankFlowSeries {
  name: string;
  colorVar: string;
  ranks: number[];
}

export interface DonutSegment {
  label: string;
  value: number;
  colorVar: string;
}

export interface SignalEvent {
  id: string;
  date: string;
  country: string;
  title: string;
  impact: "up" | "down" | "info";
  impactLabel: string;
  source: string;
}

export interface PassportData {
  reference: string;
  fromName: string;
  fromFlag: string;
  toName: string;
  toFlag: string;
  baseScore: number;
  taxTreatyBonus: number;
  nomadBonus: number;
  visaLabel: string;
  timezoneShift: string;
  confidence: number;
  verifiedOn: string;
}

export interface MetricHighlight {
  id: string;
  name: string;
  tag: string;
  description: string;
  value: string;
  unit: string;
  accent: "gold" | "blue" | "terra";
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
  trustScore: number;
  catalog: CatalogCountry[];
  driftBoard: DriftBoardRow[];
  heatmap: HeatmapData;
  rankFlow: RankFlowSeries[];
  donutSegments: DonutSegment[];
  signalEvents: SignalEvent[];
  tickerItems: string[];
  passport: PassportData;
  metricHighlights: MetricHighlight[];
  quarterSignals: { label: string; value: number }[];
  riskGauge: { value: number; label: string };
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

function driftStatusFor(value: number): DriftBoardRow["status"] {
  if (value > 2.5) return "pos";
  if (value > 0.8) return "mild";
  if (value < -1.5) return "neg";
  return "stable";
}

function driftStatusLabelFor(status: DriftBoardRow["status"]): string {
  if (status === "pos") return "Улучшается";
  if (status === "mild") return "Умеренно вверх";
  if (status === "neg") return "Ухудшается";
  return "Стабильно";
}

/** Shuffle 1..n so every rank appears exactly once per column. */
function shuffledRanks(count: number): number[] {
  const ranks = Array.from({ length: count }, (_, i) => i + 1);
  for (let i = ranks.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [ranks[i], ranks[j]] = [ranks[j], ranks[i]];
  }
  return ranks;
}

const SIGNAL_TEMPLATES: Array<{
  title: (name: string) => string;
  impact: SignalEvent["impact"];
  impactLabel: string;
  source: string;
}> = [
  {
    title: (name) => `${name} · упрощение визового режима для специалистов`,
    impact: "up",
    impactLabel: "Позитивно · релокация, найм",
    source: "Реестр мигр. права",
  },
  {
    title: (name) => `${name} · ограничение иностранных счетов`,
    impact: "down",
    impactLabel: "Высокое влияние · инвесторы",
    source: "Фин. регулятор",
  },
  {
    title: (name) => `${name} · снижение корп. налога`,
    impact: "up",
    impactLabel: "Позитивно · бизнес, фриланс",
    source: "Налог. вестник",
  },
  {
    title: (name) => `${name} · дрейф сменился на «умеренно вверх»`,
    impact: "info",
    impactLabel: "Смена дрейфа · алерт подписчикам",
    source: "Country Drift",
  },
  {
    title: (name) => `${name} · ужесточение правил аренды жилья`,
    impact: "down",
    impactLabel: "Среднее влияние · мигранты",
    source: "Жилищный реестр",
  },
  {
    title: (name) => `${name} · новая программа ВНЖ за инвестиции`,
    impact: "up",
    impactLabel: "Позитивно · резидентство",
    source: "Иммиграц. служба",
  },
];

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

  const trustScore = Math.round(
    trustDimensions.reduce((sum, dimension) => sum + dimension.value, 0) /
      trustDimensions.length,
  );

  const driftBoard: DriftBoardRow[] = FICTIONAL_COUNTRIES.map((country) => {
    const timeline = randomWalk(16, randomInRange(-2, 2), 0, 1.4);
    const driftValue =
      Math.round((timeline[timeline.length - 1] - timeline[0]) * 10) / 10;
    const status = driftStatusFor(driftValue);
    return {
      slug: country.id,
      name: country.name,
      flag: country.flag,
      timeline,
      driftValue,
      status,
      statusLabel: driftStatusLabelFor(status),
    };
  });

  const heatmap: HeatmapData = {
    rows: FICTIONAL_COUNTRIES.map((country) => country.name),
    columns: HEATMAP_MONTHS,
    values: FICTIONAL_COUNTRIES.map(() => {
      const base = randomInRange(15, 45);
      return HEATMAP_MONTHS.map(() =>
        Math.round(Math.min(100, Math.max(0, base + randomInRange(-18, 40)))),
      );
    }),
  };

  const rankColorVars = [
    "--color-gold",
    "--color-blue3",
    "--color-sage3",
    "--color-terra3",
    "--color-plum3",
  ];
  const rankColumns = RANK_QUARTERS.map(() =>
    shuffledRanks(FICTIONAL_COUNTRIES.length),
  );
  const rankFlow: RankFlowSeries[] = FICTIONAL_COUNTRIES.map(
    (country, countryIndex) => ({
      name: country.name,
      colorVar: rankColorVars[countryIndex % rankColorVars.length],
      ranks: rankColumns.map((column) => column[countryIndex]),
    }),
  );

  const donutRaw = [
    { label: "Межд. организации", colorVar: "--color-gold" },
    { label: "Нац. реестры", colorVar: "--color-blue3" },
    { label: "Правовые сигналы", colorVar: "--color-sage3" },
    { label: "Сообщество", colorVar: "--color-plum3" },
  ].map((segment) => ({
    ...segment,
    value: Math.round(randomInRange(10, 40)),
  }));
  const donutTotal = donutRaw.reduce((sum, segment) => sum + segment.value, 0);
  const donutSegments: DonutSegment[] = donutRaw.map((segment) => ({
    ...segment,
    value: Math.round((segment.value / donutTotal) * 100),
  }));

  const shuffledCountries = [...FICTIONAL_COUNTRIES].sort(
    () => Math.random() - 0.5,
  );
  const signalEvents: SignalEvent[] = SIGNAL_TEMPLATES.map(
    (template, index) => {
      const country = shuffledCountries[index % shuffledCountries.length];
      const day = Math.max(1, 28 - index * 5);
      return {
        id: `sig-${versionCounter}-${index}`,
        date: `2026-0${Math.max(1, 7 - Math.floor(index / 2))}-${String(day).padStart(2, "0")}`,
        country: country.name,
        title: template.title(country.name),
        impact: template.impact,
        impactLabel: template.impactLabel,
        source: template.source,
      };
    },
  );

  const tickerItems = signalEvents.map(
    (event) => `${event.date} · ${event.title}`,
  );

  const passport: PassportData = {
    reference: `CA-DP-2026-${String(400 + versionCounter).padStart(4, "0")}`,
    fromName: "Кариндор",
    fromFlag: "KDR",
    toName: "Аврелия",
    toFlag: "AVR",
    baseScore: Math.round(randomInRange(58, 74)),
    taxTreatyBonus: Math.round(randomInRange(6, 12)),
    nomadBonus: Math.round(randomInRange(4, 9)),
    visaLabel: "Безвиз · 180 дней",
    timezoneShift: "+1ч",
    confidence: Math.round(randomInRange(0.82, 0.94) * 100) / 100,
    verifiedOn: "2026-07",
  };

  const metricHighlights: MetricHighlight[] = [
    {
      id: "lvi",
      name: "Индекс скорости права",
      tag: "LVI · из правовых сигналов",
      description:
        "Частота изменений законодательства относительно исторической нормы. Отклонение в любую сторону повышает риск.",
      value: randomInRange(4, 8).toFixed(1),
      unit: "сигналов / квартал",
      accent: "gold",
    },
    {
      id: "ssrs",
      name: "Сценарный риск",
      tag: "SSRS · на сценарий",
      description:
        "Риск под конкретный жизненный сценарий с учётом затронутых групп и свежести каждого события.",
      value: ["Низкий", "Средний"][Math.round(Math.random())],
      unit: "для цифровых кочевников",
      accent: "blue",
    },
    {
      id: "cs",
      name: "Индекс противоречий",
      tag: "CS · из свидетельств",
      description:
        "Разброс между источниками по одной теме. Высокий балл — честное «данным верить с оговоркой» вместо ложной точности.",
      value: randomInRange(0.08, 0.4).toFixed(2),
      unit: "низкий разброс",
      accent: "terra",
    },
  ];

  const quarterSignals = RANK_QUARTERS.map((label) => ({
    label,
    value: Math.round(randomInRange(18, 92)),
  }));

  const riskGaugeValue = Math.round(randomInRange(18, 78));
  const riskGauge = {
    value: riskGaugeValue,
    label:
      riskGaugeValue < 34
        ? "Низкий"
        : riskGaugeValue < 62
          ? "Умеренный"
          : "Повышенный",
  };

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
    trustScore,
    catalog,
    driftBoard,
    heatmap,
    rankFlow,
    donutSegments,
    signalEvents,
    tickerItems,
    passport,
    metricHighlights,
    quarterSignals,
    riskGauge,
  };
}
