import { isApiError } from "../../shared/api";
import type { SupportedLocale } from "../../shared/lib/locale";

const FALLBACK_MESSAGE: Record<SupportedLocale, string> = {
  en: "An error occurred.",
  ru: "Произошла ошибка.",
  es: "Se produjo un error.",
};

export function migrationBoardErrorMessage(
  error: unknown,
  locale: SupportedLocale,
): string | undefined {
  if (isApiError(error)) {
    return typeof error.error?.message === "string"
      ? error.error.message
      : FALLBACK_MESSAGE[locale];
  }
  if (error instanceof Error) {
    return error.message;
  }
  return undefined;
}
