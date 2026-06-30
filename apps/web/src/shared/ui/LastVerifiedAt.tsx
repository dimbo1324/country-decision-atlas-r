type LastVerifiedAtProps = {
  date: string | null | undefined;
};

export function LastVerifiedAt({ date }: LastVerifiedAtProps) {
  if (!date) {
    return (
      <span className="last-verified-at last-verified-unknown">
        Дата последней проверки неизвестна
      </span>
    );
  }
  const formatted = new Date(date).toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  return <span className="last-verified-at">Данные проверены: {formatted}</span>;
}
