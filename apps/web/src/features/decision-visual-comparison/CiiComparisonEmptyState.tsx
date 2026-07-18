import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

type Props = {
  message?: string;
};

export function CiiComparisonEmptyState({ message }: Props) {
  const t = useTranslations("ciiComparison");
  return <EmptyState message={message ?? t("empty")} />;
}
