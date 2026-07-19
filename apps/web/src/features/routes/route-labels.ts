import type { RouteType } from "../../shared/api/routes";
import type { SupportedLocale } from "../../shared/lib/locale";

export const ROUTE_TYPE_LABELS: Record<
  SupportedLocale,
  Record<RouteType, string>
> = {
  en: {
    temporary_residence: "Temporary residence",
    permanent_residence: "Permanent residence",
    citizenship: "Citizenship",
    digital_nomad: "Digital nomad",
    work: "Work",
    business: "Business",
    study: "Study",
    investment: "Investment",
  },
  ru: {
    temporary_residence: "Временное проживание",
    permanent_residence: "ПМЖ",
    citizenship: "Гражданство",
    digital_nomad: "Digital nomad",
    work: "Работа",
    business: "Бизнес",
    study: "Учёба",
    investment: "Инвестиции",
  },
  es: {
    temporary_residence: "Residencia temporal",
    permanent_residence: "Residencia permanente",
    citizenship: "Ciudadanía",
    digital_nomad: "Nómada digital",
    work: "Trabajo",
    business: "Negocios",
    study: "Estudios",
    investment: "Inversión",
  },
};
