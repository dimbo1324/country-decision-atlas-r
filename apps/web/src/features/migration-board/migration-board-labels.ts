import type { SupportedLocale } from "../../shared/lib/locale";

export const TIMELINE_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    "": "Any timeline",
    "0_3_months": "0-3 months",
    "3_6_months": "3-6 months",
    "6_12_months": "6-12 months",
    "12_plus_months": "12+ months",
    "unknown": "Not sure yet",
  },
  ru: {
    "": "Любой срок",
    "0_3_months": "0-3 месяца",
    "3_6_months": "3-6 месяцев",
    "6_12_months": "6-12 месяцев",
    "12_plus_months": "12+ месяцев",
    "unknown": "Пока не знаю",
  },
  es: {
    "": "Cualquier plazo",
    "0_3_months": "0-3 meses",
    "3_6_months": "3-6 meses",
    "6_12_months": "6-12 meses",
    "12_plus_months": "12+ meses",
    "unknown": "Aún no lo sé",
  },
};

export const GOAL_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    "": "Any goal",
    "info_exchange": "Information exchange",
    "travel_together": "Travel together",
    "housing_search": "Housing search",
    "document_support": "Document support",
    "study_group": "Study group",
    "business_network": "Business network",
    "family_network": "Family network",
  },
  ru: {
    "": "Любая цель",
    "info_exchange": "Обмен информацией",
    "travel_together": "Поездка вместе",
    "housing_search": "Поиск жилья",
    "document_support": "Документы",
    "study_group": "Учёба",
    "business_network": "Бизнес",
    "family_network": "Семья",
  },
  es: {
    "": "Cualquier objetivo",
    "info_exchange": "Intercambio de información",
    "travel_together": "Viajar juntos",
    "housing_search": "Búsqueda de vivienda",
    "document_support": "Apoyo con documentos",
    "study_group": "Grupo de estudio",
    "business_network": "Red de negocios",
    "family_network": "Red familiar",
  },
};

export const STAGE_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    researching: "Researching",
    preparing_documents: "Preparing documents",
    applying: "Applying",
    waiting_decision: "Awaiting decision",
    relocating_soon: "Relocating soon",
    already_relocated: "Already relocated",
    on_hold: "On hold",
  },
  ru: {
    researching: "Изучаю",
    preparing_documents: "Готовлю документы",
    applying: "Подаюсь",
    waiting_decision: "Жду решение",
    relocating_soon: "Скоро переезжаю",
    already_relocated: "Уже переехал",
    on_hold: "На паузе",
  },
  es: {
    researching: "Investigando",
    preparing_documents: "Preparando documentos",
    applying: "Solicitando",
    waiting_decision: "Esperando decisión",
    relocating_soon: "Mudanza próxima",
    already_relocated: "Ya me mudé",
    on_hold: "En pausa",
  },
};

export const VISIBILITY_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    members_only: "Members only",
    public: "Public",
    private: "Private",
  },
  ru: {
    members_only: "Только участники",
    public: "Публично",
    private: "Приватно",
  },
  es: {
    members_only: "Solo miembros",
    public: "Público",
    private: "Privado",
  },
};
