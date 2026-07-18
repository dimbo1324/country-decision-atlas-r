import { useLocale } from "next-intl";
import { asSupportedLocale, type SupportedLocale } from "./locale";

export function useAppLocale(): SupportedLocale {
  return asSupportedLocale(useLocale());
}
