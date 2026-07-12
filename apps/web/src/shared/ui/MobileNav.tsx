"use client";

import { Drawer } from "vaul";
import { Menu, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { AppNavigation } from "./AppNavigation";
import { AuthNav } from "./AuthNav";
import { LocaleSwitcher } from "./LocaleSwitcher";

export function MobileNav() {
  const t = useTranslations("nav");
  const [open, setOpen] = useState(false);

  return (
    <Drawer.Root
      direction="right"
      open={open}
      onOpenChange={setOpen}
    >
      <Drawer.Trigger asChild>
        <button
          type="button"
          aria-label={t("openMenu")}
          className="border-warm text-c2 flex h-9 w-9 items-center justify-center border md:hidden"
          data-testid="mobile-nav-trigger"
        >
          <Menu
            width={16}
            height={16}
            strokeWidth={1.5}
          />
        </button>
      </Drawer.Trigger>
      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 z-[80] bg-black/60 backdrop-blur-[3px]" />
        <Drawer.Content
          className="bg-bg4 border-warm fixed inset-y-0 right-0 z-[81] flex h-full w-full max-w-xs flex-col border-l outline-none"
          data-testid="mobile-nav-drawer"
        >
          <div className="border-warm flex items-center justify-between border-b p-5">
            <Drawer.Title className="font-mono text-c3 text-[10px] tracking-[0.2em] uppercase">
              Country Decision Atlas
            </Drawer.Title>
            <Drawer.Close asChild>
              <button
                type="button"
                aria-label={t("closeMenu")}
                className="border-warm text-c2 flex h-8 w-8 items-center justify-center border"
              >
                <X
                  width={14}
                  height={14}
                  strokeWidth={1.5}
                />
              </button>
            </Drawer.Close>
          </div>
          <AppNavigation
            className="flex-col items-start gap-1 p-5"
            onNavigate={() => setOpen(false)}
          />
          <div className="border-warm mt-auto flex flex-col gap-4 border-t p-5">
            <AuthNav
              className="flex-col items-start gap-3"
              onNavigate={() => setOpen(false)}
            />
            <LocaleSwitcher />
          </div>
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer.Root>
  );
}
