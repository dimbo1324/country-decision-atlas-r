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
  /** Plain next/link, not next-intl's — this component also renders from
   * /internal/** pages that sit outside NextIntlClientProvider, where the
   * intl Link would throw. Callers inside the [locale] tree must pass an
   * already-prefixed path (e.g. via `getPathname({ href, locale })` from
   * `i18n/navigation`), not a bare route. */
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
