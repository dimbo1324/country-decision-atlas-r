import { describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api/admin-country-proposals", () => ({
  adminCountryProposalsApi: { listAdminCountryProposals: vi.fn() },
}));

import { adminCountryProposalsApi } from "../../shared/api/admin-country-proposals";
import { adminCountryProposalsQuery } from "./api";

describe("adminCountryProposalsQuery", () => {
  it("keys by status when one is given", () => {
    expect(adminCountryProposalsQuery("published").queryKey).toEqual([
      "admin",
      "country-proposals",
      "published",
    ]);
  });

  it("keys by 'all' when no status is given", () => {
    expect(adminCountryProposalsQuery().queryKey).toEqual([
      "admin",
      "country-proposals",
      "all",
    ]);
  });

  it("delegates its queryFn to the API client with the given status", () => {
    const options = adminCountryProposalsQuery("draft");
    options.queryFn?.({} as never);
    expect(
      adminCountryProposalsApi.listAdminCountryProposals,
    ).toHaveBeenCalledWith("draft");
  });
});
