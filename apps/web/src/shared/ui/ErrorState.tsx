import Link from "next/link";
import { ErrorState as ErrorStateShell } from "@country-decision-atlas/ui";

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
    <ErrorStateShell
      title={isBackendDown ? "Backend недоступен" : "Что-то пошло не так"}
      code={code}
      message={
        isBackendDown
          ? "API недоступен. Убедитесь, что backend запущен, и повторите попытку."
          : message
      }
      action={
        backHref && (
          <Link
            href={backHref}
            className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          >
            {backLabel ?? "Назад"}
          </Link>
        )
      }
    />
  );
}
