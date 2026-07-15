import { describe, expect, it } from "vitest";
import { isFeatureEnabled } from "./features";
import type { FeatureFlag } from "../api/feature-flags";

function flag(key: string, enabled: boolean): FeatureFlag {
  return {
    key,
    name: key,
    status: "enabled",
    access_tier: "public",
    default_enabled: enabled,
    is_enabled_for_context: enabled,
    decision_reason: "test-fixture",
  };
}

describe("isFeatureEnabled", () => {
  it("returns true when the key is enabled in an array response", () => {
    const features = [flag("trips", true)];
    expect(isFeatureEnabled(features, "trips")).toBe(true);
  });

  it("returns true when the key is enabled in an {items} response", () => {
    const features = {
      items: [flag("trips", true)],
      context: {
        access_tier: "public" as const,
        environment: "test",
        is_admin: false,
      },
    };
    expect(isFeatureEnabled(features, "trips")).toBe(true);
  });

  it("returns false when the key is present but disabled", () => {
    const features = [flag("trips", false)];
    expect(isFeatureEnabled(features, "trips")).toBe(false);
  });

  it("returns false when the key is not found", () => {
    const features = [flag("trips", true)];
    expect(isFeatureEnabled(features, "watchlist")).toBe(false);
  });

  it("returns false for null or undefined input", () => {
    expect(isFeatureEnabled(null, "trips")).toBe(false);
    expect(isFeatureEnabled(undefined, "trips")).toBe(false);
  });
});
