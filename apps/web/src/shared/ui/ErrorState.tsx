type ApiErrorShape = {
  error?: {
    code?: string;
    message?: string;
  };
};

type ErrorStateProps = {
  error?: ApiErrorShape | string;
};

export function ErrorState({ error }: ErrorStateProps) {
  if (typeof error === "string") {
    return (
      <div className="errorState">
        <strong>Something went wrong.</strong>
        <span>{error}</span>
      </div>
    );
  }
  const code = error?.error?.code;
  const message = error?.error?.message ?? "An unexpected error occurred.";
  return (
    <div className="errorState">
      <strong>Something went wrong.</strong>
      {code && <span className="errorCode">{code}</span>}
      <span>{message}</span>
    </div>
  );
}
