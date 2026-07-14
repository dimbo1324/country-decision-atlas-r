import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { authApi } from "../../shared/api/auth";

const SESSIONS_QUERY_KEY = ["account", "sessions"] as const;
const SECURITY_NOTIFICATIONS_QUERY_KEY = [
  "account",
  "security-notifications",
] as const;
const TELEGRAM_STATUS_QUERY_KEY = ["account", "telegram-status"] as const;
const ME_QUERY_KEY = ["account", "me"] as const;

export function meQuery() {
  return queryOptions({
    queryKey: ME_QUERY_KEY,
    queryFn: () => authApi.getMe(),
    staleTime: 60_000,
  });
}

export function sessionsQuery() {
  return queryOptions({
    queryKey: SESSIONS_QUERY_KEY,
    queryFn: () => authApi.listSessions(),
    staleTime: 15_000,
  });
}

export function securityNotificationsQuery() {
  return queryOptions({
    queryKey: SECURITY_NOTIFICATIONS_QUERY_KEY,
    queryFn: () => authApi.listSecurityNotifications(),
    staleTime: 15_000,
  });
}

export function telegramStatusQuery() {
  return queryOptions({
    queryKey: TELEGRAM_STATUS_QUERY_KEY,
    queryFn: () => authApi.getTelegramLinkStatus(),
    staleTime: 15_000,
  });
}

export function useRevokeSessionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => authApi.revokeSession(sessionId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: SESSIONS_QUERY_KEY });
    },
  });
}

export function useRevokeAllSessionsMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (currentPassword: string) =>
      authApi.revokeAllSessions(currentPassword),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: SESSIONS_QUERY_KEY });
    },
  });
}

export function useAcknowledgeSecurityNotificationMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notificationId: string) =>
      authApi.acknowledgeSecurityNotification(notificationId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: SECURITY_NOTIFICATIONS_QUERY_KEY,
      });
    },
  });
}

export function useLinkTelegramMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (code: string) => authApi.linkTelegram(code),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: TELEGRAM_STATUS_QUERY_KEY,
      });
    },
  });
}

export function useUnlinkTelegramMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => authApi.unlinkTelegram(),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: TELEGRAM_STATUS_QUERY_KEY,
      });
    },
  });
}
