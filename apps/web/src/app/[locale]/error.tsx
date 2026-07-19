"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { Button, ErrorState } from "@country-decision-atlas/ui";

type Props = {
  error: Error & { digest?: string };
  reset: () => void;
};

// Segment-local boundary: inside /[locale]/**, NextIntlClientProvider is
// available (unlike the root app/error.tsx, which deliberately avoids
// next-intl since it also has to catch errors from /internal/** and truly
// locale-less paths). Next.js prefers this nearer boundary for errors
// thrown while rendering anything under [locale].
export default function LocaleError({ error, reset }: Props) {
  const t = useTranslations("error");

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <ErrorState
        title={t("title")}
        code={error.digest}
        message={t("message")}
        action={
          <Button
            variant="ghost"
            onClick={reset}
          >
            {t("retry")}
          </Button>
        }
      />
    </div>
  );
}
