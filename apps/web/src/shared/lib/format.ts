/** The whole UI is Russian; every date/time helper formats in ru-RU so
 * English month names never appear inside Russian copy. */
export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("ru-RU");
}

export function formatScore(value: number): string {
  return `${Math.round(value)}/100`;
}

export function formatWeight(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}

export function capitalize(value: string): string {
  return value.length === 0 ? value : value[0].toUpperCase() + value.slice(1);
}
