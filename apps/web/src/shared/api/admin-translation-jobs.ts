import type { components } from "@country-decision-atlas/contracts/generated/types";
import { csrfHeaders } from "../auth/session";
import { apiGet, apiPost } from "./http";

export type TranslationJobItem = components["schemas"]["TranslationJobItem"];
export type TranslationJobListResponse =
  components["schemas"]["TranslationJobListResponse"];
export type TranslationJobCreateMissingRequest =
  components["schemas"]["TranslationJobCreateMissingRequest"];
export type TranslationJobCreateStaleRequest =
  components["schemas"]["TranslationJobCreateStaleRequest"];
export type TranslationJobCreateResponse =
  components["schemas"]["TranslationJobCreateResponse"];
export type TranslationJobProcessBatchRequest =
  components["schemas"]["TranslationJobProcessBatchRequest"];
export type TranslationJobBatchResult =
  components["schemas"]["TranslationJobBatchResult"];
export type TranslationJobRetryFailedRequest =
  components["schemas"]["TranslationJobRetryFailedRequest"];
export type TranslationJobRetryFailedResponse =
  components["schemas"]["TranslationJobRetryFailedResponse"];

export function listAdminTranslationJobs(): Promise<TranslationJobListResponse> {
  return apiGet<TranslationJobListResponse>("/api/v1/admin/translation-jobs", {
    headers: csrfHeaders(),
  });
}

export function createMissingTranslationJobs(
  payload: TranslationJobCreateMissingRequest,
): Promise<TranslationJobCreateResponse> {
  return apiPost<
    TranslationJobCreateResponse,
    TranslationJobCreateMissingRequest
  >("/api/v1/admin/translation-jobs/create-missing", payload, {
    headers: csrfHeaders(),
  });
}

export function createStaleTranslationJobs(
  payload: TranslationJobCreateStaleRequest,
): Promise<TranslationJobCreateResponse> {
  return apiPost<
    TranslationJobCreateResponse,
    TranslationJobCreateStaleRequest
  >("/api/v1/admin/translation-jobs/create-stale", payload, {
    headers: csrfHeaders(),
  });
}

export function processTranslationJobBatch(
  payload: TranslationJobProcessBatchRequest,
): Promise<TranslationJobBatchResult> {
  return apiPost<TranslationJobBatchResult, TranslationJobProcessBatchRequest>(
    "/api/v1/admin/translation-jobs/process-batch",
    payload,
    { headers: csrfHeaders() },
  );
}

export function retryFailedTranslationJobs(
  payload: TranslationJobRetryFailedRequest,
): Promise<TranslationJobRetryFailedResponse> {
  return apiPost<
    TranslationJobRetryFailedResponse,
    TranslationJobRetryFailedRequest
  >("/api/v1/admin/translation-jobs/retry-failed", payload, {
    headers: csrfHeaders(),
  });
}

export const adminTranslationJobsApi = {
  listAdminTranslationJobs,
  createMissingTranslationJobs,
  createStaleTranslationJobs,
  processTranslationJobBatch,
  retryFailedTranslationJobs,
};
