import { Badge } from "./Badge";
import type { SupportedLocale } from "../lib/locale";
import { useAppLocale } from "../lib/useAppLocale";

type BadgeVariant =
  | "default"
  | "positive"
  | "negative"
  | "warning"
  | "critical"
  | "info";

const STATUS_VARIANTS: Record<string, BadgeVariant> = {
  published: "positive",
  valid: "positive",
  passed: "positive",
  draft: "warning",
  review: "info",
  warning: "warning",
  invalid: "critical",
  failed: "critical",
  archived: "default",
};

const STATUS_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    published: "Published",
    valid: "Valid",
    passed: "Passed",
    draft: "Draft",
    review: "In review",
    warning: "Warning",
    invalid: "Invalid",
    failed: "Failed",
    archived: "Archived",
    active: "Active",
    inactive: "Inactive",
    pending: "Pending",
    approved: "Approved",
    rejected: "Rejected",
    critical: "Critical",
    medium: "Medium",
    low: "Low",
    high: "High",
    ok: "OK",
  },
  ru: {
    published: "Опубликовано",
    valid: "Действует",
    passed: "Пройдено",
    draft: "Черновик",
    review: "На проверке",
    warning: "Предупреждение",
    invalid: "Недействительно",
    failed: "Ошибка",
    archived: "Архив",
    active: "Активно",
    inactive: "Неактивно",
    pending: "В ожидании",
    approved: "Одобрено",
    rejected: "Отклонено",
    critical: "Критично",
    medium: "Средний",
    low: "Низкий",
    high: "Высокий",
    ok: "Норма",
  },
  es: {
    published: "Publicado",
    valid: "Vigente",
    passed: "Superado",
    draft: "Borrador",
    review: "En revisión",
    warning: "Advertencia",
    invalid: "No válido",
    failed: "Error",
    archived: "Archivado",
    active: "Activo",
    inactive: "Inactivo",
    pending: "Pendiente",
    approved: "Aprobado",
    rejected: "Rechazado",
    critical: "Crítico",
    medium: "Medio",
    low: "Bajo",
    high: "Alto",
    ok: "Correcto",
  },
};

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const locale = useAppLocale();
  return (
    <Badge variant={STATUS_VARIANTS[status] ?? "default"}>
      {STATUS_LABELS[locale][status] ?? status}
    </Badge>
  );
}
