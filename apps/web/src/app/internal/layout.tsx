import { NextIntlClientProvider } from "next-intl";
import { InternalShell } from "../../shared/ui/InternalShell";
import messages from "../../messages/ru.json";

// /internal/** sits outside [locale]/layout.tsx's NextIntlClientProvider by
// design -- this route tree stays untranslated (owner-confirmed scope
// boundary, see task-checklist.md). But several shared/ui components
// (ErrorBoundary, LoadingState, EmptyState, ...) unconditionally call
// useTranslations() since the i18n migration, and previously had no intl
// context here at all -- any error or loading state on an internal page
// would throw "No intl context found" instead of rendering. Providing the
// existing ru.json catalog (this route tree's own established language
// before and after the migration) gives those shared components a working
// context without translating /internal/** itself.
export default function InternalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <NextIntlClientProvider
      locale="ru"
      messages={messages}
    >
      <InternalShell>{children}</InternalShell>
    </NextIntlClientProvider>
  );
}
