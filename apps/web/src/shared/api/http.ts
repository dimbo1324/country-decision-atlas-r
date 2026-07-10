import type { components } from "@country-decision-atlas/contracts/generated/types";
import { API_BASE_URL, API_TIMEOUT_MS } from "../config/env";

export type ApiErrorResponse = components["schemas"]["ErrorResponse"];

type RequestOptions = {
  headers?: HeadersInit;
};

function toNetworkApiError(err: unknown): ApiErrorResponse {
  if (
    err instanceof DOMException &&
    (err.name === "TimeoutError" || err.name === "AbortError")
  ) {
    return {
      error: {
        code: "request_timeout",
        message: `Превышено время ожидания ответа от сервера (${API_TIMEOUT_MS / 1000} с).`,
      },
    };
  }
  return {
    error: {
      code: "network_error",
      message:
        err instanceof Error
          ? err.message
          : "Сетевая ошибка при обращении к API.",
    },
  };
}

async function fetchWithTimeout(
  path: string,
  init: RequestInit,
): Promise<Response> {
  try {
    return await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: AbortSignal.timeout(API_TIMEOUT_MS),
    });
  } catch (err) {
    throw toNetworkApiError(err);
  }
}

export function queryString(
  params: Record<string, string | number | boolean | null | undefined>,
): string {
  const searchParams = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  }

  const encoded = searchParams.toString();
  return encoded ? `?${encoded}` : "";
}

export function isApiError(e: unknown): e is ApiErrorResponse {
  return (
    typeof e === "object" &&
    e !== null &&
    "error" in (e as Record<string, unknown>)
  );
}

async function parseJsonSafe<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (text === "") {
    return undefined as T;
  }
  try {
    return JSON.parse(text) as T;
  } catch {
    throw new Error(`Unexpected non-JSON response (HTTP ${response.status})`);
  }
}

export async function apiGet<TResponse>(
  path: string,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetchWithTimeout(path, {
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
    cache: "no-store",
    credentials: "include",
  });

  if (!response.ok) {
    throw await parseJsonSafe<ApiErrorResponse>(response);
  }

  return parseJsonSafe<TResponse>(response);
}

export async function apiPost<TResponse, TBody>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetchWithTimeout(path, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: JSON.stringify(body),
    cache: "no-store",
    credentials: "include",
  });

  if (!response.ok) {
    throw await parseJsonSafe<ApiErrorResponse>(response);
  }

  return parseJsonSafe<TResponse>(response);
}

export async function apiPatch<TResponse, TBody>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetchWithTimeout(path, {
    method: "PATCH",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: JSON.stringify(body),
    cache: "no-store",
    credentials: "include",
  });

  if (!response.ok) {
    throw await parseJsonSafe<ApiErrorResponse>(response);
  }

  return parseJsonSafe<TResponse>(response);
}

export async function apiDelete<TResponse>(
  path: string,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetchWithTimeout(path, {
    method: "DELETE",
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
    cache: "no-store",
    credentials: "include",
  });

  if (!response.ok) {
    throw await parseJsonSafe<ApiErrorResponse>(response);
  }

  return parseJsonSafe<TResponse>(response);
}
