import { Badge } from "./Badge";

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

const STATUS_LABELS_RU: Record<string, string> = {
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
};

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANTS[status] ?? "default"}>
      {STATUS_LABELS_RU[status] ?? status}
    </Badge>
  );
}
