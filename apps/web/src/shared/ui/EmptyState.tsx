type EmptyStateProps = {
  message?: string;
};

export function EmptyState({
  message = "Данные отсутствуют.",
}: EmptyStateProps) {
  return <p className="notice emptyNotice">{message}</p>;
}
