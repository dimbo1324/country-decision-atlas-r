type DisclaimerNoticeProps = {
  text?: string;
};

const DEFAULT_DISCLAIMER =
  "Это индикатор качества данных, а не рекомендация. Не является юридической консультацией.";

export function DisclaimerNotice({
  text = DEFAULT_DISCLAIMER,
}: DisclaimerNoticeProps) {
  return (
    <p
      className="disclaimer-notice"
      role="note"
    >
      {text}
    </p>
  );
}
