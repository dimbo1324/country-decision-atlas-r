import Link from "next/link";

type ApiErrorShape = {
  error?: {
    code?: string;
    message?: string;
  };
};

type ErrorStateProps = {
  error?: ApiErrorShape | string;
  backHref?: string;
  backLabel?: string;
};

export function ErrorState({ error, backHref, backLabel }: ErrorStateProps) {
  let code: string | undefined;
  let message: string;

  if (typeof error === "string") {
    message = error || "Произошла непредвиденная ошибка.";
  } else {
    code = error?.error?.code;
    message = error?.error?.message ?? "Произошла непредвиденная ошибка.";
  }

  const isBackendDown =
    message.toLowerCase().includes("fetch failed") ||
    message.toLowerCase().includes("econnrefused") ||
    message.toLowerCase().includes("failed to fetch");

  return (
    <div className="errorState">
      <strong className="errorTitle">
        {isBackendDown ? "Backend недоступен" : "Что-то пошло не так"}
      </strong>
      {code && <span className="errorCode">{code}</span>}
      <span className="errorMessage">
        {isBackendDown
          ? "API недоступен. Убедитесь, что backend запущен, и повторите попытку."
          : message}
      </span>
      {backHref && (
        <Link
          href={backHref}
          className="errorBack"
        >
          {backLabel ?? "Назад"}
        </Link>
      )}
    </div>
  );
}
