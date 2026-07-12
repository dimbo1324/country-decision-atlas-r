import Link from "next/link";

// /internal is the ops console — Stage 12 gives it its own dedicated shell
// (compact top bar, queue sidebar, role-guard). Until then it gets this
// minimal wrapper rather than the public AppShell, which depends on
// next-intl context this route deliberately sits outside of.
export default function InternalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative z-[1] flex min-h-screen flex-col">
      <header className="border-warm bg-bg/85 sticky top-0 z-40 border-b px-6 py-4 backdrop-blur-md">
        <Link
          href="/"
          className="font-mono text-c3 hover:text-c1 text-[10px] tracking-[0.2em] uppercase transition-colors duration-300"
        >
          ← Country Decision Atlas
        </Link>
      </header>
      <main className="mx-auto w-full max-w-[1400px] flex-1 px-6 py-8">
        {children}
      </main>
    </div>
  );
}
