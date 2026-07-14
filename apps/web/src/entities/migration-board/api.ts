import {
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import type {
  BoardPostFilters,
  CreateContactRequestRequest,
  CreateMigrationBoardPostRequest,
  CreateMigrationBoardReportRequest,
  ModerateMigrationBoardPostRequest,
  ReviewMigrationBoardReportRequest,
  UpdateMigrationBoardPostRequest,
} from "../../shared/api/migrationBoard";
import { migrationBoardApi } from "../../shared/api/migrationBoard";

const BOARD_POSTS_QUERY_KEY = (filters: BoardPostFilters) =>
  ["migration-board", "posts", filters] as const;
const BOARD_POST_QUERY_KEY = (postId: string) =>
  ["migration-board", "post", postId] as const;
const MY_POSTS_QUERY_KEY = ["migration-board", "my-posts"] as const;
const CONTACT_REQUESTS_INCOMING_KEY = [
  "migration-board",
  "contact-requests",
  "incoming",
] as const;
const CONTACT_REQUESTS_OUTGOING_KEY = [
  "migration-board",
  "contact-requests",
  "outgoing",
] as const;
const ADMIN_POSTS_QUERY_KEY = (status?: string) =>
  ["migration-board", "admin", "posts", status ?? "all"] as const;
const ADMIN_REPORTS_QUERY_KEY = [
  "migration-board",
  "admin",
  "reports",
] as const;

export function boardPostsQuery(filters: BoardPostFilters) {
  return queryOptions({
    queryKey: BOARD_POSTS_QUERY_KEY(filters),
    queryFn: () => migrationBoardApi.listBoardPosts(filters),
    staleTime: 15_000,
  });
}

export function boardPostQuery(postId: string) {
  return queryOptions({
    queryKey: BOARD_POST_QUERY_KEY(postId),
    queryFn: () => migrationBoardApi.getBoardPost(postId),
    enabled: Boolean(postId),
  });
}

export function myBoardPostsQuery() {
  return queryOptions({
    queryKey: MY_POSTS_QUERY_KEY,
    queryFn: () => migrationBoardApi.listMyBoardPosts(),
  });
}

export function incomingContactRequestsQuery() {
  return queryOptions({
    queryKey: CONTACT_REQUESTS_INCOMING_KEY,
    queryFn: () => migrationBoardApi.listIncomingContactRequests(),
  });
}

export function outgoingContactRequestsQuery() {
  return queryOptions({
    queryKey: CONTACT_REQUESTS_OUTGOING_KEY,
    queryFn: () => migrationBoardApi.listOutgoingContactRequests(),
  });
}

export function adminBoardPostsQuery(status?: string) {
  return queryOptions({
    queryKey: ADMIN_POSTS_QUERY_KEY(status),
    queryFn: () => migrationBoardApi.listAdminBoardPosts(status),
  });
}

export function adminBoardReportsQuery() {
  return queryOptions({
    queryKey: ADMIN_REPORTS_QUERY_KEY,
    queryFn: () => migrationBoardApi.listAdminBoardReports(),
  });
}

export function useCreateBoardPostMutation() {
  return useMutation({
    mutationFn: (payload: CreateMigrationBoardPostRequest) =>
      migrationBoardApi.createBoardPost(payload),
  });
}

export function useUpdateBoardPostMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      postId,
      payload,
    }: {
      postId: string;
      payload: UpdateMigrationBoardPostRequest;
    }) => migrationBoardApi.updateBoardPost(postId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_POSTS_QUERY_KEY });
    },
  });
}

export function useSubmitBoardPostMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (postId: string) => migrationBoardApi.submitBoardPost(postId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_POSTS_QUERY_KEY });
    },
  });
}

export function useArchiveBoardPostMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (postId: string) => migrationBoardApi.archiveBoardPost(postId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: MY_POSTS_QUERY_KEY });
    },
  });
}

export function useCreateContactRequestMutation() {
  return useMutation({
    mutationFn: ({
      postId,
      payload,
    }: {
      postId: string;
      payload: CreateContactRequestRequest;
    }) => migrationBoardApi.createContactRequest(postId, payload),
  });
}

function useInvalidateContactRequests() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({
      queryKey: CONTACT_REQUESTS_INCOMING_KEY,
    });
    void queryClient.invalidateQueries({
      queryKey: CONTACT_REQUESTS_OUTGOING_KEY,
    });
  };
}

export function useAcceptContactRequestMutation() {
  const invalidate = useInvalidateContactRequests();
  return useMutation({
    mutationFn: (requestId: string) =>
      migrationBoardApi.acceptContactRequest(requestId),
    onSuccess: invalidate,
  });
}

export function useDeclineContactRequestMutation() {
  const invalidate = useInvalidateContactRequests();
  return useMutation({
    mutationFn: (requestId: string) =>
      migrationBoardApi.declineContactRequest(requestId),
    onSuccess: invalidate,
  });
}

export function useCancelContactRequestMutation() {
  const invalidate = useInvalidateContactRequests();
  return useMutation({
    mutationFn: (requestId: string) =>
      migrationBoardApi.cancelContactRequest(requestId),
    onSuccess: invalidate,
  });
}

export function useReportPostMutation() {
  return useMutation({
    mutationFn: ({
      postId,
      payload,
    }: {
      postId: string;
      payload: CreateMigrationBoardReportRequest;
    }) => migrationBoardApi.reportPost(postId, payload),
  });
}

function useInvalidateAdminBoard() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({
      queryKey: ["migration-board", "admin"],
    });
  };
}

export function useApproveAdminBoardPostMutation() {
  const invalidate = useInvalidateAdminBoard();
  return useMutation({
    mutationFn: (postId: string) =>
      migrationBoardApi.approveAdminBoardPost(postId),
    onSuccess: invalidate,
  });
}

export function useRejectAdminBoardPostMutation() {
  const invalidate = useInvalidateAdminBoard();
  return useMutation({
    mutationFn: ({
      postId,
      payload,
    }: {
      postId: string;
      payload: ModerateMigrationBoardPostRequest;
    }) => migrationBoardApi.rejectAdminBoardPost(postId, payload),
    onSuccess: invalidate,
  });
}

export function useHideAdminBoardPostMutation() {
  const invalidate = useInvalidateAdminBoard();
  return useMutation({
    mutationFn: ({
      postId,
      payload,
    }: {
      postId: string;
      payload: ModerateMigrationBoardPostRequest;
    }) => migrationBoardApi.hideAdminBoardPost(postId, payload),
    onSuccess: invalidate,
  });
}

export function useResolveAdminBoardReportMutation() {
  const invalidate = useInvalidateAdminBoard();
  return useMutation({
    mutationFn: ({
      reportId,
      payload,
    }: {
      reportId: string;
      payload: ReviewMigrationBoardReportRequest;
    }) => migrationBoardApi.resolveAdminBoardReport(reportId, payload),
    onSuccess: invalidate,
  });
}

export function useDismissAdminBoardReportMutation() {
  const invalidate = useInvalidateAdminBoard();
  return useMutation({
    mutationFn: ({
      reportId,
      payload,
    }: {
      reportId: string;
      payload: ReviewMigrationBoardReportRequest;
    }) => migrationBoardApi.dismissAdminBoardReport(reportId, payload),
    onSuccess: invalidate,
  });
}
