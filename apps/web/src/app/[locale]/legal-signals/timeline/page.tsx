import { getLocale } from "next-intl/server";
import { redirect } from "../../../../i18n/navigation";

export const dynamic = "force-dynamic";

type PageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

/** `/legal-signals/timeline` was folded into a tab
 * (`/legal-signals?tab=timeline`) on the registry page -- this route stays
 * only to redirect old bookmarks/links, carrying over the shared filter
 * params (country_slug, signal_type, impact_direction, impact_level, year)
 * so a saved filtered link keeps its meaning. */
export default async function LegalSignalsTimelineRedirectPage({
  searchParams,
}: PageProps) {
  const params = await searchParams;
  const locale = await getLocale();
  const query: Record<string, string> = { tab: "timeline" };
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === "string") {
      query[key] = value;
    }
  }
  redirect({ href: { pathname: "/legal-signals", query }, locale });
}
