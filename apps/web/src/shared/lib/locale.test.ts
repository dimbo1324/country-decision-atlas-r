import { describe, expect, it } from "vitest";
import { asSupportedLocale, DEFAULT_LOCALE } from "./locale";

describe("asSupportedLocale", () => {
  it("passes through a supported locale unchanged", () => {
    expect(asSupportedLocale("en")).toBe("en");
    expect(asSupportedLocale("ru")).toBe("ru");
  });

  it("falls back to the default locale for an unsupported value", () => {
    expect(asSupportedLocale("fr")).toBe(DEFAULT_LOCALE);
    expect(asSupportedLocale("")).toBe(DEFAULT_LOCALE);
  });
});
