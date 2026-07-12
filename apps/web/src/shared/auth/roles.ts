import type { AuthUser } from "../api/auth";

export const ADMIN_ROLES = new Set(["editor", "admin", "owner"]);
export const MODERATION_ROLES = new Set(["moderator", "admin", "owner"]);
export const DATA_QUALITY_ROLES = ADMIN_ROLES;

export function hasRole(user: AuthUser | null, roles: Set<string>): boolean {
  return user !== null && roles.has(user.role);
}
