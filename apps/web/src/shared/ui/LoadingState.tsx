import { LoadingState as LoadingStateShell } from "@country-decision-atlas/ui";

type LoadingStateProps = {
  message?: string;
};

export function LoadingState({
  message = "Загрузка данных…",
}: LoadingStateProps) {
  return <LoadingStateShell message={message} />;
}
