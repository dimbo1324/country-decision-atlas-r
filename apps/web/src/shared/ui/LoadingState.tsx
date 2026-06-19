type LoadingStateProps = {
  message?: string;
};

export function LoadingState({ message = "Loading data…" }: LoadingStateProps) {
  return (
    <div className="loadingState">
      <span className="loadingDot" aria-hidden="true" />
      <span className="loadingDot" aria-hidden="true" />
      <span className="loadingDot" aria-hidden="true" />
      <p className="loadingMessage">{message}</p>
    </div>
  );
}
