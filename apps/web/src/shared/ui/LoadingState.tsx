type LoadingStateProps = {
  message?: string;
};

export function LoadingState({ message = "Загрузка данных…" }: LoadingStateProps) {
  return (
    <div className="loadingState">
      <span className="loadingDot" aria-hidden="true" />
      <span className="loadingDot" aria-hidden="true" />
      <span className="loadingDot" aria-hidden="true" />
      <p className="loadingMessage">{message}</p>
    </div>
  );
}
