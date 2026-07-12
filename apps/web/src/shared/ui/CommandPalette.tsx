"use client";

import { Command } from "cmdk";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { useAuth } from "../auth/AuthProvider";
import { useRouter } from "../../i18n/navigation";
import { routes } from "../lib/routes";

/** Static ⌘K shell: sections + navigation only. Wiring this to live
 * `/search` results is Stage 5 (search page) work — this is the palette
 * frame the plan asks for ahead of that. */
export function CommandPalette() {
  const t = useTranslations("search");
  const tNav = useTranslations("nav");
  const tAuth = useTranslations("auth");
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((prev) => !prev);
      }
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  function go(href: string) {
    setOpen(false);
    router.push(href);
  }

  const sections = [
    {
      label: t("sectionSections"),
      items: [
        { label: tNav("countries"), href: routes.countries },
        { label: tNav("decision"), href: routes.decision },
        { label: tNav("migrationBoard"), href: routes.migrationBoard },
        { label: tNav("legalSignals"), href: routes.legalSignals },
        { label: tNav("sources"), href: routes.sources },
      ],
    },
    {
      label: t("sectionActions"),
      items: user
        ? [{ label: tAuth("account"), href: routes.account }]
        : [{ label: tAuth("signIn"), href: routes.login }],
    },
  ];

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="border-warm text-c3 hover:border-warm-hi hover:text-c1 font-mono hidden items-center gap-2 border px-3 py-2 text-[10px] tracking-[0.15em] uppercase transition-colors duration-300 sm:inline-flex"
        data-testid="command-palette-trigger"
      >
        <Search
          width={13}
          height={13}
          strokeWidth={1.5}
        />
        {t("paletteTrigger")}
        <kbd className="text-c4 border-warm border px-1 py-0.5 text-[9px]">
          ⌘K
        </kbd>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-[95] flex items-start justify-center bg-black/60 pt-[15vh] backdrop-blur-sm"
          onClick={() => setOpen(false)}
          data-testid="command-palette-overlay"
        >
          <Command
            className="bg-bg4 border-warm-hi w-full max-w-lg border shadow-[0_24px_64px_rgb(0_0_0/0.5)]"
            onClick={(event) => event.stopPropagation()}
            label={t("paletteTitle")}
          >
            <Command.Input
              autoFocus
              placeholder={t("placeholder")}
              className="border-warm text-c1 placeholder:text-c4 font-body w-full border-b bg-transparent px-4 py-3.5 text-sm outline-none"
            />
            <Command.List className="scrollbar-thin max-h-80 overflow-y-auto p-2">
              <Command.Empty className="text-c4 font-mono px-3 py-6 text-center text-[10px] tracking-[0.15em] uppercase">
                {t("paletteEmpty")}
              </Command.Empty>
              {sections.map((section) => (
                <Command.Group
                  key={section.label}
                  heading={section.label}
                  className="[&_[cmdk-group-heading]]:text-c4 [&_[cmdk-group-heading]]:font-mono [&_[cmdk-group-heading]]:px-3 [&_[cmdk-group-heading]]:py-2 [&_[cmdk-group-heading]]:text-[9px] [&_[cmdk-group-heading]]:tracking-[0.2em] [&_[cmdk-group-heading]]:uppercase"
                >
                  {section.items.map((item) => (
                    <Command.Item
                      key={item.href}
                      onSelect={() => go(item.href)}
                      className="text-c2 data-[selected=true]:bg-bg3 data-[selected=true]:text-c1 font-body cursor-pointer px-3 py-2.5 text-sm outline-none"
                    >
                      {item.label}
                    </Command.Item>
                  ))}
                </Command.Group>
              ))}
            </Command.List>
          </Command>
        </div>
      )}
    </>
  );
}
