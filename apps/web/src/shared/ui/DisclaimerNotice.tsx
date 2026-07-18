import { useTranslations } from "next-intl";

type DisclaimerNoticeProps = {
  text?: string;
};

export function DisclaimerNotice({ text }: DisclaimerNoticeProps) {
  const t = useTranslations("disclaimerNotice");
  return (
    <p
      className="disclaimer-notice"
      role="note"
    >
      {text ?? t("default")}
    </p>
  );
}
