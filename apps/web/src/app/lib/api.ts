const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: string };

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
    });
    if (!response.ok) {
      return { ok: false, error: `Request failed with ${response.status}` };
    }
    return { ok: true, data: (await response.json()) as T };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Backend request failed",
    };
  }
}

export async function apiPost<TResponse, TBody>(
  path: string,
  body: TBody,
): Promise<ApiResult<TResponse>> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    if (!response.ok) {
      return { ok: false, error: `Request failed with ${response.status}` };
    }
    return { ok: true, data: (await response.json()) as TResponse };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Backend request failed",
    };
  }
}
