import { notFound } from "next/navigation";

// Catches every otherwise-unmatched path under a valid /[locale] prefix
// (typo'd or dead links, removed pages) and explicitly calls `notFound()`
// from *inside* the [locale] segment tree. Without this, Next's automatic
// 404 handling for a path with no matching page.tsx anywhere never
// descends into [locale]'s layout at all -- it always falls through to the
// root app/not-found.tsx (hardcoded Russian), even for a perfectly valid
// /en/... or /es/... URL. Calling notFound() here is what makes the nearer
// [locale]/not-found.tsx boundary reachable.
export default function CatchAll(): never {
  notFound();
}
