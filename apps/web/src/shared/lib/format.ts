export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString("en", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatScore(value: number): string {
  return `${Math.round(value)}/100`;
}

export function formatWeight(value: number): string {
  return `${(value * 100).toFixed(0)}%`;
}
