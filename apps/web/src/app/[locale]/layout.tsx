import type { ReactNode } from "react";
import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import {
  getMessages,
  getTranslations,
  setRequestLocale,
} from "next-intl/server";
import { notFound } from "next/navigation";
import { routing } from "../../i18n/routing";
import { GlossaryProvider } from "../../shared/glossary/GlossaryProvider";
import { AppShell } from "../../shared/ui/AppShell";

type LocaleLayoutProps = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "metadata" });
  return { description: t("description") };
}

export default async function LocaleLayout({
  children,
  params,
}: LocaleLayoutProps) {
  const { locale } = await params;
  if (!routing.locales.includes(locale as (typeof routing.locales)[number])) {
    notFound();
  }
  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    // `locale` is passed explicitly (not left to next-intl's auto-
    // inheritance): the header lives inside a `<Suspense>` streaming
    // boundary, and without the explicit prop the client provider can
    // initialize before the inherited locale is available and fall back to
    // `defaultLocale`. That made every next-intl `<Link>` in the header
    // build `/en/...` hrefs on a `/ru` (or `/es`) page, diverging from the
    // server-rendered `/ru/...` HTML — the header hydration mismatch.
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
    >
      <GlossaryProvider>
        <AppShell>{children}</AppShell>
      </GlossaryProvider>
    </NextIntlClientProvider>
  );
}
