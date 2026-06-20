import { API_BASE_URL } from "../../shared/config/env";

export type ApiResult<T> = { ok: true; data: T } | { ok: false; error: string };

type ApiRequestOptions<TBody> = {
  method?: "POST";
  body?: TBody;
};

async function apiRequest<TResponse, TBody = never>(
  path: string,
  options: ApiRequestOptions<TBody> = {},
): Promise<ApiResult<TResponse>> {
  try {
    const requestInit: RequestInit = {
      cache: "no-store",
    };

    if (options.method) {
      requestInit.method = options.method;
    }
    if (options.body !== undefined) {
      requestInit.headers = { "content-type": "application/json" };
      requestInit.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...requestInit,
    });
    if (!response.ok) {
      return { ok: false, error: `Запрос завершился с ошибкой ${response.status}` };
    }
    return { ok: true, data: (await response.json()) as TResponse };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Ошибка запроса к серверу",
    };
  }
}

export async function apiGet<T>(path: string): Promise<ApiResult<T>> {
  return apiRequest<T>(path);
}

export async function apiPost<TResponse, TBody>(
  path: string,
  body: TBody,
): Promise<ApiResult<TResponse>> {
  return apiRequest<TResponse, TBody>(path, { method: "POST", body });
}
