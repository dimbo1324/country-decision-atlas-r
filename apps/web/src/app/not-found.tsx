import { Button, ErrorState } from "@country-decision-atlas/ui";
import Link from "next/link";

// Deliberately no next-intl here: this can render for /internal/** routes
// too (outside NextIntlClientProvider), and for genuinely locale-less
// paths the middleware never matched to a [locale] segment.
export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center p-8">
      <ErrorState
        title="Страница не найдена"
        message="Такой страницы не существует или она была перемещена."
        action={
          <Link href="/">
            <Button variant="ghost">На главную</Button>
          </Link>
        }
      />
    </div>
  );
}
