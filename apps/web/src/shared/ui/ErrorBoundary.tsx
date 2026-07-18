"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";
import { useTranslations } from "next-intl";
import { Button, Card, Kicker } from "@country-decision-atlas/ui";
import { trackEvent } from "../analytics/client";

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  error: Error | null;
};

/** Split out so the translated fallback text can use `useTranslations()` —
 * the boundary itself must stay a class component (no hook equivalent for
 * `componentDidCatch`), and hooks can't be called from one. */
function ErrorBoundaryFallback({ onRetry }: { onRetry: () => void }) {
  const t = useTranslations("errorBoundary");
  return (
    <div
      className="flex min-h-[40vh] items-center justify-center py-12"
      data-testid="app-error-boundary"
    >
      <Card
        interactive={false}
        className="flex max-w-md flex-col gap-4 text-center"
      >
        <Kicker>{t("kicker")}</Kicker>
        <p className="text-c1 text-sm leading-relaxed">{t("message")}</p>
        <Button
          type="button"
          onClick={onRetry}
          data-testid="app-error-boundary-retry"
        >
          {t("retry")}
        </Button>
      </Card>
    </div>
  );
}

/** React error boundaries must be class components -- there is no hook
 * equivalent for componentDidCatch. Reports a `client_error` analytics
 * event (best-effort, matching Stage 13's plan item) and renders a plain
 * retry UI instead of a blank screen. Deliberately calls the low-level
 * `trackEvent` client directly rather than the `useAnalyticsEvent` hook,
 * since hooks are unavailable in a class component. */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    void trackEvent({
      event_type: "client_error",
      source: "web",
      path:
        typeof window !== "undefined" ? window.location.pathname : undefined,
      metadata: {
        message: error.message,
        stack: error.stack?.slice(0, 2000),
        component_stack: info.componentStack?.slice(0, 2000),
      },
    });
  }

  handleRetry = () => {
    this.setState({ error: null });
  };

  render() {
    if (!this.state.error) {
      return this.props.children;
    }

    return <ErrorBoundaryFallback onRetry={this.handleRetry} />;
  }
}
