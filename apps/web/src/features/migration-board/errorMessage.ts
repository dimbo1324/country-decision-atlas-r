import { isApiError } from "../../shared/api";

export function migrationBoardErrorMessage(error: unknown): string | undefined {
  if (isApiError(error)) {
    return typeof error.error?.message === "string"
      ? error.error.message
      : "Произошла ошибка.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return undefined;
}
