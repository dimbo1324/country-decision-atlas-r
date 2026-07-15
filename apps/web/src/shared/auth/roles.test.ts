import { describe, expect, it } from "vitest";
import type { AuthUser } from "../api/auth";
import {
  ADMIN_ROLES,
  DATA_QUALITY_ROLES,
  MODERATION_ROLES,
  STRICT_ADMIN_ROLES,
  hasRole,
} from "./roles";

function user(role: string): AuthUser {
  return { role } as AuthUser;
}

describe("hasRole", () => {
  it("returns false for a signed-out user", () => {
    expect(hasRole(null, ADMIN_ROLES)).toBe(false);
  });

  it("accepts every admin-tier role for ADMIN_ROLES", () => {
    for (const role of ["editor", "admin", "owner"]) {
      expect(hasRole(user(role), ADMIN_ROLES)).toBe(true);
    }
  });

  it("rejects regular users and moderators for ADMIN_ROLES", () => {
    expect(hasRole(user("user"), ADMIN_ROLES)).toBe(false);
    expect(hasRole(user("moderator"), ADMIN_ROLES)).toBe(false);
  });

  it("accepts moderators and admins for MODERATION_ROLES", () => {
    for (const role of ["moderator", "admin", "owner"]) {
      expect(hasRole(user(role), MODERATION_ROLES)).toBe(true);
    }
    expect(hasRole(user("editor"), MODERATION_ROLES)).toBe(false);
  });

  it("excludes editor from STRICT_ADMIN_ROLES, matching backend require_admin", () => {
    expect(hasRole(user("editor"), STRICT_ADMIN_ROLES)).toBe(false);
    expect(hasRole(user("admin"), STRICT_ADMIN_ROLES)).toBe(true);
    expect(hasRole(user("owner"), STRICT_ADMIN_ROLES)).toBe(true);
  });

  it("keeps DATA_QUALITY_ROLES aliased to ADMIN_ROLES", () => {
    expect(DATA_QUALITY_ROLES).toBe(ADMIN_ROLES);
  });
});
