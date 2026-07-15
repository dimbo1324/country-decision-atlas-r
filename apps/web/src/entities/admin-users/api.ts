import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { adminUsersApi } from "../../shared/api/admin-users";
import type {
  RoleUpdateRequest,
  UserStatusUpdateRequest,
} from "../../shared/api/admin-users";

const QUERY_KEY = ["admin", "users"] as const;
const sessionsQueryKey = (userId: string) =>
  ["admin", "users", userId, "sessions"] as const;

export function adminUsersQuery() {
  return queryOptions({
    queryKey: QUERY_KEY,
    queryFn: () => adminUsersApi.listAdminUsers(),
  });
}

export function userSessionsQuery(userId: string) {
  return queryOptions({
    queryKey: sessionsQueryKey(userId),
    queryFn: () => adminUsersApi.listUserSessions(userId),
    enabled: Boolean(userId),
  });
}

function useInvalidate() {
  const queryClient = useQueryClient();
  return () => void queryClient.invalidateQueries({ queryKey: QUERY_KEY });
}

export function useUpdateUserRoleMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      userId,
      payload,
    }: {
      userId: string;
      payload: RoleUpdateRequest;
    }) => adminUsersApi.updateUserRole(userId, payload),
    onSuccess: invalidate,
  });
}

export function useUpdateUserStatusMutation() {
  const invalidate = useInvalidate();
  return useMutation({
    mutationFn: ({
      userId,
      payload,
    }: {
      userId: string;
      payload: UserStatusUpdateRequest;
    }) => adminUsersApi.updateUserStatus(userId, payload),
    onSuccess: invalidate,
  });
}

export function useRevokeAllUserSessionsMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => adminUsersApi.revokeAllUserSessions(userId),
    onSuccess: (_data, userId) => {
      void queryClient.invalidateQueries({
        queryKey: sessionsQueryKey(userId),
      });
    },
  });
}
