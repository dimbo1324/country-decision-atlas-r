import { describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api/decision", () => ({
  decisionApi: { runDecision: vi.fn(), resolveWizard: vi.fn() },
}));
vi.mock("../../shared/api/scenarios", () => ({
  scenariosApi: { listScenarios: vi.fn() },
}));
vi.mock("../../shared/api/personas", () => ({
  personasApi: { listPersonas: vi.fn() },
}));
vi.mock("../../shared/api/cii", () => ({
  ciiApi: { compareCountriesCii: vi.fn(), getMatrix: vi.fn() },
}));
vi.mock("../../shared/api/countries", () => ({
  countriesApi: { listCountries: vi.fn() },
}));

import { countriesApi } from "../../shared/api/countries";
import {
  allCountriesQuery,
  compareCiiQuery,
  matrixQuery,
  personasQuery,
  scenariosQuery,
} from "./api";

describe("allCountriesQuery", () => {
  it("keys by locale and requests the API's max page size", () => {
    const options = allCountriesQuery("en");
    expect(options.queryKey).toEqual(["country", "list", "all", "en"]);

    options.queryFn?.({} as never);
    expect(countriesApi.listCountries).toHaveBeenCalledWith({
      locale: "en",
      limit: 100,
    });
  });
});

describe("scenariosQuery / personasQuery", () => {
  it("key by locale", () => {
    expect(scenariosQuery("ru").queryKey).toEqual(["scenarios", "ru"]);
    expect(personasQuery("ru").queryKey).toEqual(["personas", "ru"]);
  });
});

describe("compareCiiQuery", () => {
  it("is enabled only with at least two countries and a scenario", () => {
    expect(
      compareCiiQuery({ countries: ["a", "b"], scenario: "s", locale: "en" })
        .enabled,
    ).toBe(true);
    expect(
      compareCiiQuery({ countries: ["a"], scenario: "s", locale: "en" })
        .enabled,
    ).toBe(false);
    expect(
      compareCiiQuery({ countries: ["a", "b"], scenario: "", locale: "en" })
        .enabled,
    ).toBe(false);
  });

  it("does not retry on failure", () => {
    expect(
      compareCiiQuery({ countries: ["a", "b"], scenario: "s", locale: "en" })
        .retry,
    ).toBe(false);
  });
});

describe("matrixQuery", () => {
  it("keys by locale and does not retry", () => {
    const options = matrixQuery("en");
    expect(options.queryKey).toEqual(["cii", "matrix", "en"]);
    expect(options.retry).toBe(false);
  });
});
