import type { ReactElement } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import { withNuqsTestingAdapter } from "nuqs/adapters/testing";
import { NextIntlClientProvider } from "next-intl";
import messages from "../messages/ru.json";

/** Fresh `QueryClient` per render, retries disabled so a mocked-error test
 * fails fast instead of waiting out TanStack Query's default retry backoff. */
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

export function renderWithProviders(
  ui: ReactElement,
  options?: { searchParams?: string } & Omit<RenderOptions, "wrapper">,
) {
  const queryClient = createTestQueryClient();
  const NuqsWrapper = withNuqsTestingAdapter({
    searchParams: options?.searchParams,
    hasMemory: true,
  });

  return render(ui, {
    wrapper: ({ children }) => (
      <NextIntlClientProvider
        locale="ru"
        messages={messages}
      >
        <QueryClientProvider client={queryClient}>
          <NuqsWrapper>{children}</NuqsWrapper>
        </QueryClientProvider>
      </NextIntlClientProvider>
    ),
    ...options,
  });
}
