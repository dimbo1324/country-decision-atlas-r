import { afterEach, describe, expect, it, vi } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../../test-utils/render";
import { HomeDeck } from "./HomeDeck";

vi.mock("./CountryOverviewCards", () => ({
  CountryOverviewCards: () => <div data-testid="mock-country-cards" />,
}));
vi.mock("./ScenarioWinnersPanel", () => ({
  ScenarioWinnersPanel: () => <div data-testid="mock-scenario-winners" />,
}));
vi.mock("./HomeMatrixPreview", () => ({
  HomeMatrixPreview: () => <div data-testid="mock-matrix-preview" />,
}));
vi.mock("./LatestLegalEventsPanel", () => ({
  LatestLegalEventsPanel: () => <div data-testid="mock-legal-events" />,
}));
vi.mock("./KeyInsightsPanel", () => ({
  KeyInsightsPanel: () => <div data-testid="mock-key-insights" />,
}));

const props = {
  countries: [],
  scenarioWinners: [],
  matrix: { scenarios: [] },
  latestLegalEvents: [],
  keyInsights: [],
} as unknown as Parameters<typeof HomeDeck>[0];

/** `matches` decides both `useMediaQuery("(min-width: 821px)")` (desktop
 * pager vs. mobile stack) and `useReducedMotion`'s query independently --
 * tests select the scenario by controlling which queries report true. */
function mockMatchMedia(matchingQueries: string[]) {
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation((query: string) => ({
      matches: matchingQueries.includes(query),
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    })),
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("HomeDeck", () => {
  it("desktop, no reduced motion: paginates via HorizontalPager and hides off-screen slides from a11y+focus", async () => {
    mockMatchMedia(["(min-width: 821px)"]);
    const user = userEvent.setup();
    renderWithProviders(<HomeDeck {...props} />);

    expect(screen.getByTestId("pager-slide-countries")).not.toHaveAttribute(
      "inert",
    );
    expect(screen.getByTestId("pager-slide-scenarios")).toHaveAttribute(
      "inert",
    );

    await user.click(screen.getByTestId("pager-next"));

    expect(screen.getByTestId("pager-slide-countries")).toHaveAttribute(
      "inert",
    );
    expect(screen.getByTestId("pager-slide-scenarios")).not.toHaveAttribute(
      "inert",
    );
    expect(screen.getByTestId("mock-scenario-winners")).toBeInTheDocument();
  });

  it("prefers-reduced-motion: renders a flat stack with no pager controls", () => {
    mockMatchMedia(["(prefers-reduced-motion: reduce)", "(min-width: 821px)"]);
    renderWithProviders(<HomeDeck {...props} />);

    expect(screen.getByTestId("mock-country-cards")).toBeInTheDocument();
    expect(screen.getByTestId("mock-scenario-winners")).toBeInTheDocument();
    expect(screen.getByTestId("mock-legal-events")).toBeInTheDocument();
    expect(screen.queryByTestId("pager-next")).not.toBeInTheDocument();
  });

  it("narrow viewport: renders MobileStack instead of HorizontalPager", () => {
    mockMatchMedia([]);
    renderWithProviders(<HomeDeck {...props} />);

    expect(screen.getByTestId("stack-slide-countries")).toBeInTheDocument();
    expect(screen.queryByTestId("pager-next")).not.toBeInTheDocument();
  });
});
