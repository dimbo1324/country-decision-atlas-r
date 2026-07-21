import { Button, ErrorState } from "@country-decision-atlas/ui";
import { useTranslations } from "next-intl";
import { Link } from "../../i18n/navigation";
import { routes } from "../../shared/lib/routes";

// Nearer boundary than the root app/not-found.tsx: this one renders inside
// `[locale]/layout.tsx`'s `NextIntlClientProvider` (which calls
// `setRequestLocale` upstream), so `useTranslations` resolves correctly
// here as a plain Server Component -- same pattern every other `[locale]`
// page already uses. The root not-found.tsx stays hardcoded-Russian on
// purpose: it also has to catch /internal/** and genuinely locale-less
// paths, which never reach this file.
export default function LocaleNotFound() {
  const t = useTranslations("notFound");

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <ErrorState
        title={t("title")}
        message={t("message")}
        action={
          <Link href={routes.home}>
            <Button variant="ghost">{t("backHome")}</Button>
          </Link>
        }
      />
    </div>
  );
}
