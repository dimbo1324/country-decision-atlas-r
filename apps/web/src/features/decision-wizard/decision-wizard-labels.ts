import type { DecisionWizardAnswers } from "../../shared/api/decision";
import type { SupportedLocale } from "../../shared/lib/locale";

export type DecisionWizardOption<T extends string> = {
  value: T;
  label: string;
};

type Level = "low" | "medium" | "high";

type DecisionWizardLabels = {
  title: string;
  hint: string;
  open: string;
  close: string;
  goal: string;
  budget: string;
  family: string;
  timeframe: string;
  workPriority: string;
  safetyPriority: string;
  citizenshipPriority: string;
  businessPriority: string;
  apply: string;
  applying: string;
  confidence: string;
  scenario: string;
  persona: string;
  noPersona: string;
  explanation: string;
  warnings: string;
  manualNote: string;
  unavailable: string;
  primaryGoalOptions: Array<
    DecisionWizardOption<DecisionWizardAnswers["primary_goal"]>
  >;
  budgetOptions: Array<DecisionWizardOption<DecisionWizardAnswers["budget_level"]>>;
  familyOptions: Array<DecisionWizardOption<DecisionWizardAnswers["family_status"]>>;
  timeframeOptions: Array<DecisionWizardOption<DecisionWizardAnswers["timeframe"]>>;
  levelOptions: Array<DecisionWizardOption<Level>>;
  warningLabels: Record<string, string>;
};

const LEVEL_OPTIONS_RU: Array<DecisionWizardOption<Level>> = [
  { value: "low", label: "Низкий" },
  { value: "medium", label: "Средний" },
  { value: "high", label: "Высокий" },
];

const LEVEL_OPTIONS_EN: Array<DecisionWizardOption<Level>> = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

export const DECISION_WIZARD_LABELS: Record<SupportedLocale, DecisionWizardLabels> = {
  ru: {
    title: "Помочь выбрать настройки",
    hint: "Ответьте на несколько вопросов, и форма подбора заполнится без сохранения профиля.",
    open: "Открыть",
    close: "Скрыть",
    goal: "Цель",
    budget: "Бюджет",
    family: "Семья",
    timeframe: "Срок",
    workPriority: "Работа",
    safetyPriority: "Безопасность",
    citizenshipPriority: "Статус",
    businessPriority: "Бизнес",
    apply: "Заполнить форму",
    applying: "Подбираем...",
    confidence: "Уверенность",
    scenario: "Сценарий",
    persona: "Персона",
    noPersona: "Без персоны",
    explanation: "Почему так",
    warnings: "Ограничения",
    manualNote: "После применения рекомендации настройки можно изменить вручную.",
    unavailable: "Мастер временно недоступен. Можно продолжить вручную.",
    primaryGoalOptions: [
      { value: "residence", label: "ВНЖ и переезд" },
      { value: "citizenship", label: "ПМЖ и гражданство" },
      { value: "low_budget", label: "Низкий бюджет" },
      { value: "business", label: "Бизнес" },
      { value: "safety", label: "Безопасность" },
      { value: "remote_work", label: "Удаленная работа" },
      { value: "study", label: "Учеба" },
    ],
    budgetOptions: [{ value: "unknown", label: "Не знаю" }, ...LEVEL_OPTIONS_RU],
    familyOptions: [
      { value: "unknown", label: "Не важно" },
      { value: "solo", label: "Один" },
      { value: "couple", label: "Пара" },
      { value: "family_with_children", label: "Семья с детьми" },
    ],
    timeframeOptions: [
      { value: "unknown", label: "Не важно" },
      { value: "fast", label: "Быстро" },
      { value: "medium", label: "Среднесрочно" },
      { value: "long", label: "Долгосрочно" },
    ],
    levelOptions: LEVEL_OPTIONS_RU,
    warningLabels: {
      recommended_persona_unavailable: "Рекомендованная персона пока недоступна.",
    },
  },
  en: {
    title: "Help me choose settings",
    hint: "Answer a few questions and the decision form will be filled without saving a profile.",
    open: "Open",
    close: "Hide",
    goal: "Goal",
    budget: "Budget",
    family: "Family",
    timeframe: "Timeline",
    workPriority: "Work",
    safetyPriority: "Safety",
    citizenshipPriority: "Status",
    businessPriority: "Business",
    apply: "Fill the form",
    applying: "Resolving...",
    confidence: "Confidence",
    scenario: "Scenario",
    persona: "Persona",
    noPersona: "No persona",
    explanation: "Why this fits",
    warnings: "Warnings",
    manualNote:
      "After applying the recommendation, you can still adjust settings manually.",
    unavailable: "Wizard is temporarily unavailable. You can continue manually.",
    primaryGoalOptions: [
      { value: "residence", label: "Residence and relocation" },
      { value: "citizenship", label: "Permanent residence and citizenship" },
      { value: "low_budget", label: "Low budget" },
      { value: "business", label: "Business" },
      { value: "safety", label: "Safety" },
      { value: "remote_work", label: "Remote work" },
      { value: "study", label: "Study" },
    ],
    budgetOptions: [{ value: "unknown", label: "Not sure" }, ...LEVEL_OPTIONS_EN],
    familyOptions: [
      { value: "unknown", label: "Does not matter" },
      { value: "solo", label: "Solo" },
      { value: "couple", label: "Couple" },
      { value: "family_with_children", label: "Family with children" },
    ],
    timeframeOptions: [
      { value: "unknown", label: "Does not matter" },
      { value: "fast", label: "Fast" },
      { value: "medium", label: "Medium term" },
      { value: "long", label: "Long term" },
    ],
    levelOptions: LEVEL_OPTIONS_EN,
    warningLabels: {
      recommended_persona_unavailable: "The recommended persona is unavailable.",
    },
  },
};
