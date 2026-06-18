import type { components } from "@country-decision-atlas/contracts/generated/types";
import { API_BASE_URL } from "../config/env";

export type ApiErrorResponse = components["schemas"]["ErrorResponse"];

type RequestOptions = {
  headers?: HeadersInit;
};

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

export async function apiGet<TResponse>(
  path: string,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json",
      ...options.headers,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw (await response.json()) as ApiErrorResponse;
  }

  return (await response.json()) as TResponse;
}

export async function apiPost<TResponse, TBody>(
  path: string,
  body: TBody,
  options: RequestOptions = {},
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...options.headers,
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });

  if (!response.ok) {
    throw (await response.json()) as ApiErrorResponse;
  }

  return (await response.json()) as TResponse;
}
