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
    message = error || "An unexpected error occurred.";
  } else {
    code = error?.error?.code;
    message = error?.error?.message ?? "An unexpected error occurred.";
  }

  const isBackendDown =
    message.toLowerCase().includes("fetch failed") ||
    message.toLowerCase().includes("econnrefused") ||
    message.toLowerCase().includes("failed to fetch");

  return (
    <div className="errorState">
      <strong className="errorTitle">
        {isBackendDown ? "Backend unavailable" : "Something went wrong"}
      </strong>
      {code && <span className="errorCode">{code}</span>}
      <span className="errorMessage">
        {isBackendDown
          ? "The API is not available right now. Check that the backend is running and try again."
          : message}
      </span>
      {backHref && (
        <Link href={backHref} className="errorBack">
          {backLabel ?? "Go back"}
        </Link>
      )}
    </div>
  );
}
