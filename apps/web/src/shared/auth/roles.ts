import type { AuthUser } from "../api/auth";

export const ADMIN_ROLES = new Set(["editor", "admin", "owner"]);
export const MODERATION_ROLES = new Set(["moderator", "admin", "owner"]);
export const DATA_QUALITY_ROLES = ADMIN_ROLES;
/** Backend `require_admin` (users admin) excludes `editor`, unlike every
 * other `/internal` queue which maps to `ADMIN_ROLES`. */
export const STRICT_ADMIN_ROLES = new Set(["admin", "owner"]);

export function hasRole(user: AuthUser | null, roles: Set<string>): boolean {
  return user !== null && roles.has(user.role);
}
