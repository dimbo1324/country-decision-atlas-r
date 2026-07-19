import type { SupportedLocale } from "./locale";

/** Shared draft/submitted/published/rejected/archived publication-status
 * labels, reused by author-metrics and country-proposals (both use the same
 * `PublicationStatus` enum). Keyed per interface locale rather than routed
 * through next-intl -- callers need an unknown-value fallback (`?? raw`)
 * for a status the frontend doesn't recognize yet. */
export const MODERATION_STATUS_LABELS: Record<
  SupportedLocale,
  Record<string, string>
> = {
  en: {
    draft: "Draft",
    submitted: "In moderation",
    published: "Published",
    rejected: "Rejected",
    archived: "Archived",
  },
  ru: {
    draft: "Черновик",
    submitted: "На модерации",
    published: "Опубликована",
    rejected: "Отклонена",
    archived: "В архиве",
  },
  es: {
    draft: "Borrador",
    submitted: "En moderación",
    published: "Publicada",
    rejected: "Rechazada",
    archived: "Archivada",
  },
};

export function moderationStatusLabel(
  status: string,
  locale: SupportedLocale,
): string {
  return MODERATION_STATUS_LABELS[locale][status] ?? status;
}
