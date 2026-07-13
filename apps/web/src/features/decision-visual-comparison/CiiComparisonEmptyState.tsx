import { EmptyState } from "../../shared/ui/EmptyState";

type Props = {
  message?: string;
};

export function CiiComparisonEmptyState({ message }: Props) {
  return (
    <EmptyState message={message ?? "Визуальное сравнение CII недоступно"} />
  );
}
