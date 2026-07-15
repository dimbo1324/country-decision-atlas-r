import { describe, expect, it } from "vitest";
import { routes } from "./routes";

describe("routes", () => {
  it("builds parameterized paths", () => {
    expect(routes.country("russia")).toBe("/countries/russia");
    expect(routes.countryProposalWizard("abc-1")).toBe(
      "/account/country-proposals/abc-1",
    );
    expect(routes.authorProfile("user-1")).toBe("/authors/user-1");
    expect(routes.migrationBoardPost("post-1")).toBe("/migration-board/post-1");
    expect(routes.tripDetail("trip-1")).toBe("/trips/trip-1");
    expect(routes.tripSharedPublic("token-1")).toBe("/trips/shared/token-1");
  });

  it("builds query-string paths for a country slug", () => {
    expect(routes.legalSignalsForCountry("russia")).toBe(
      "/legal-signals?country_slug=russia",
    );
    expect(routes.sourcesForCountry("russia")).toBe(
      "/sources?country_slug=russia",
    );
  });

  it("keeps static routes locale-agnostic and bare", () => {
    expect(routes.home).toBe("/");
    expect(routes.countries).toBe("/countries");
  });
});
