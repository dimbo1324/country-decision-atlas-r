"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_SECTIONS: {
  title: string;
  items: { href: string; label: string }[];
}[] = [
  {
    title: "Модерация",
    items: [
      { href: "/internal/community-moderation", label: "Сообщество" },
      { href: "/internal/migration-board-moderation", label: "Борд миграции" },
      {
        href: "/internal/author-metrics-moderation",
        label: "Авторские метрики",
      },
      { href: "/internal/country-proposals", label: "Заявки стран" },
    ],
  },
  {
    title: "Данные",
    items: [
      { href: "/internal/data-quality", label: "Качество данных" },
      { href: "/internal/contradiction-candidates", label: "Противоречия" },
      { href: "/internal/ai-drafts", label: "AI-черновики" },
      { href: "/internal/evidence", label: "Источники и сигналы" },
    ],
  },
  {
    title: "Операции",
    items: [
      { href: "/internal/users", label: "Пользователи" },
      { href: "/internal/translation-jobs", label: "Переводы" },
      { href: "/internal/recompute", label: "Пересчёт" },
    ],
  },
];

export function InternalShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="relative z-[1] flex min-h-screen flex-col">
      <header className="border-warm bg-bg/90 sticky top-0 z-40 flex items-center justify-between border-b px-6 py-3 backdrop-blur-md">
        <Link
          href="/"
          className="font-mono text-c3 hover:text-c1 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          ← Country Decision Atlas
        </Link>
        <span className="font-mono text-c4 text-[10px] tracking-[0.3em] uppercase">
          Служебный контур
        </span>
      </header>
      <div className="mx-auto flex w-full max-w-[1400px] flex-1 gap-6 px-6 py-6">
        <nav
          className="border-warm hidden w-56 shrink-0 flex-col gap-6 border-r pr-4 lg:flex"
          data-testid="internal-sidebar"
        >
          {NAV_SECTIONS.map((section) => (
            <div
              key={section.title}
              className="flex flex-col gap-1.5"
            >
              <span className="font-mono text-c4 px-2 text-[9px] tracking-[0.25em] uppercase">
                {section.title}
              </span>
              {section.items.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`px-2 py-1.5 text-sm transition-colors duration-200 ${
                      active
                        ? "bg-bg3 text-gold3 border-gold2/60 border-l-2"
                        : "text-c3 hover:text-c1 border-l-2 border-transparent"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>
        <main className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
