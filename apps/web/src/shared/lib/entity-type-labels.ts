import type { SearchResultItem } from "../api/search";
import type { SupportedLocale } from "./locale";

/** Names of searchable entity types, shared by the ⌘K palette and the
 * /search result cards. Keyed per interface locale rather than routed
 * through next-intl -- callers need an unknown-value fallback (`?? raw`)
 * for entity types the frontend doesn't recognize yet, which next-intl's
 * `t()` can't express without a try/catch at every call site. */
export const ENTITY_TYPE_LABELS: Record<
  SupportedLocale,
  Record<SearchResultItem["entity_type"], string>
> = {
  en: {
    country: "Country",
    route: "Route",
    route_checklist_item: "Checklist item",
    legal_signal: "Legal signal",
    source: "Source",
    evidence_item: "Evidence",
    country_pair_compatibility: "Country compatibility",
    methodology: "Methodology",
    glossary_term: "Glossary term",
  },
  ru: {
    country: "Страна",
    route: "Маршрут",
    route_checklist_item: "Пункт чек-листа",
    legal_signal: "Правовой сигнал",
    source: "Источник",
    evidence_item: "Доказательство",
    country_pair_compatibility: "Совместимость стран",
    methodology: "Методология",
    glossary_term: "Термин глоссария",
  },
  es: {
    country: "País",
    route: "Ruta",
    route_checklist_item: "Punto de la lista",
    legal_signal: "Señal legal",
    source: "Fuente",
    evidence_item: "Evidencia",
    country_pair_compatibility: "Compatibilidad de países",
    methodology: "Metodología",
    glossary_term: "Término del glosario",
  },
};

export function entityTypeLabel(
  entityType: SearchResultItem["entity_type"],
  locale: SupportedLocale,
): string {
  return ENTITY_TYPE_LABELS[locale][entityType] ?? entityType;
}
