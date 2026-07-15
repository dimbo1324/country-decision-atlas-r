import type { SearchResultItem } from "../api/search";

/** Single source for the Russian names of searchable entity types,
 * shared by the ⌘K palette and the /search result cards. */
export const ENTITY_TYPE_LABELS: Record<
  SearchResultItem["entity_type"],
  string
> = {
  country: "Страна",
  route: "Маршрут",
  route_checklist_item: "Пункт чек-листа",
  legal_signal: "Правовой сигнал",
  source: "Источник",
  evidence_item: "Доказательство",
  country_pair_compatibility: "Совместимость стран",
  methodology: "Методология",
  glossary_term: "Термин глоссария",
};

export function entityTypeLabel(
  entityType: SearchResultItem["entity_type"],
): string {
  return ENTITY_TYPE_LABELS[entityType] ?? entityType;
}
