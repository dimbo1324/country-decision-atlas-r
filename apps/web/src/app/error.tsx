"use client";

import { useEffect } from "react";
import { Button, ErrorState } from "@country-decision-atlas/ui";

type Props = {
  error: Error & { digest?: string };
  reset: () => void;
};

// Deliberately no next-intl here: this boundary can catch errors from
// anywhere in the tree, including /internal/** routes that sit outside
// NextIntlClientProvider — a translation hook here would itself throw.
export default function GlobalError({ error, reset }: Props) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <ErrorState
        title="Что-то пошло не так"
        code={error.digest}
        message="Произошла непредвиденная ошибка. Попробуйте обновить страницу."
        action={
          <Button
            variant="ghost"
            onClick={reset}
          >
            Повторить
          </Button>
        }
      />
    </div>
  );
}
