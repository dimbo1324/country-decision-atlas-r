import { useTranslations } from "next-intl";
import { LoadingState as LoadingStateShell } from "@country-decision-atlas/ui";

type LoadingStateProps = {
  message?: string;
};

export function LoadingState({ message }: LoadingStateProps) {
  const t = useTranslations("loadingState");
  return <LoadingStateShell message={message ?? t("default")} />;
}
