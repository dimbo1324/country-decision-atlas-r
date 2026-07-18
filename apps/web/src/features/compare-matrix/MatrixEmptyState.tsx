import { useTranslations } from "next-intl";
import { EmptyState } from "../../shared/ui/EmptyState";

type Props = {
  message?: string;
};

export function MatrixEmptyState({ message }: Props) {
  const t = useTranslations("compareMatrix");
  return (
    <div data-testid="compare-matrix-empty">
      <EmptyState message={message ?? t("empty")} />
    </div>
  );
}
