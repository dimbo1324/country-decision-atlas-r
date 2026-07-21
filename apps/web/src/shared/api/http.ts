import type { components } from "@country-decision-atlas/contracts/generated/types";
import { API_BASE_URL, API_TIMEOUT_MS } from "../config/env";
import {
  asSupportedLocale,
  DEFAULT_LOCALE,
  type SupportedLocale,
} from "../lib/locale";

export type ApiErrorResponse = components["schemas"]["ErrorResponse"];

type RequestOptions = {
  headers?: HeadersInit;
};

/** `apiGet`/`apiPost`/etc run deep inside ~70 data-fetching modules with no
 * natural place to receive a `locale` argument (most aren't React code at
 * all), so this reads it straight from the URL instead of threading it
 * through every call site -- `routing.ts`'s `localePrefix: "always"`
 * guarantees the first path segment is always the interface locale on the
 * client. Falls back to the default locale during SSR/build, where these
 * network-error messages are never actually shown to a user. */
function currentPathLocale(): SupportedLocale {
  if (typeof window === "undefined") return DEFAULT_LOCALE;
  const segment = window.location.pathname.split("/")[1] ?? "";
  return asSupportedLocale(segment);
}

const NETWORK_ERROR_MESSAGES: Record<
  SupportedLocale,
  { timeout: (seconds: number) => string; network: string }
> = {
  en: {
    timeout: (seconds) => `The server took too long to respond (${seconds}s).`,
    network: "Network error while contacting the API.",
  },
  ru: {
    timeout: (seconds) =>
      `Превышено время ожидания ответа от сервера (${seconds} с).`,
    network: "Сетевая ошибка при обращении к API.",
  },
  es: {
    timeout: (seconds) =>
      `El servidor tardó demasiado en responder (${seconds} s).`,
    network: "Error de red al conectar con la API.",
  },
};

function toNetworkApiError(err: unknown): ApiErrorResponse {
  const messages = NETWORK_ERROR_MESSAGES[currentPathLocale()];
  if (
    err instanceof DOMException &&
    (err.name === "TimeoutError" || err.name === "AbortError")
  ) {
    return {
      error: {
        code: "request_timeout",
        message: messages.timeout(API_TIMEOUT_MS / 1000),
      },
    };
  }
  return {
    error: {
      code: "network_error",
      message: err instanceof Error ? err.message : messages.network,
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

const GENERIC_MUTATION_ERROR: Record<SupportedLocale, string> = {
  en: "The action could not be completed. Please try again.",
  ru: "Не удалось выполнить действие. Попробуйте ещё раз.",
  es: "No se pudo completar la acción. Inténtalo de nuevo.",
};

/** Best-effort human-readable message for a failed mutation, for the many
 * modules (entities/*'s `useMutation` `onError`s) that aren't React
 * components and so can't call `useTranslations()` -- same
 * `currentPathLocale()` fallback the network-error messages above use. */
export function mutationErrorMessage(err: unknown): string {
  if (isApiError(err) && err.error?.message) {
    return err.error.message;
  }
  return GENERIC_MUTATION_ERROR[currentPathLocale()];
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

export async function apiPut<TResponse, TBody>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetchWithTimeout(path, {
    method: "PUT",
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
