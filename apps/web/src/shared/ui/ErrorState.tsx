import Link from "next/link";
import { useTranslations } from "next-intl";
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
  const t = useTranslations("errorState");
  let code: string | undefined;
  let message: string;

  if (typeof error === "string") {
    message = error || t("genericMessage");
  } else {
    code = error?.error?.code;
    message = error?.error?.message ?? t("genericMessage");
  }

  const isBackendDown =
    message.toLowerCase().includes("fetch failed") ||
    message.toLowerCase().includes("econnrefused") ||
    message.toLowerCase().includes("failed to fetch");

  return (
    <ErrorStateShell
      title={isBackendDown ? t("backendDownTitle") : t("genericTitle")}
      code={code}
      message={isBackendDown ? t("backendDownMessage") : message}
      action={
        backHref && (
          <Link
            href={backHref}
            className="font-mono text-gold3 hover:text-gold text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
          >
            {backLabel ?? t("backLabel")}
          </Link>
        )
      }
    />
  );
}
