import { describe, expect, it, vi } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { components } from "@country-decision-atlas/contracts/generated/types";
import { renderWithProviders } from "../../test-utils/render";
import { CountryDossier } from "./CountryDossier";

vi.mock("../../shared/features/FeatureProvider", () => ({
  useFeatureEnabled: () => true,
}));
vi.mock("../community", () => ({
  CommunityCountryBlock: () => <div data-testid="mock-community" />,
}));
vi.mock("../country-drift", () => ({
  CountryDriftBlock: () => <div data-testid="mock-drift" />,
}));
vi.mock("../data-journal", () => ({
  CountryDataJournalBlock: () => <div data-testid="mock-data-journal" />,
}));
vi.mock("../migration-board", () => ({
  CountryMigrationBoardBlock: () => <div data-testid="mock-migration-board" />,
}));
vi.mock("../platform-intelligence", () => ({
  PlatformIntelligenceBlock: () => <div data-testid="mock-platform-intel" />,
}));
vi.mock("../routes", () => ({
  CountryRoutesBlock: () => <div data-testid="mock-routes" />,
}));
vi.mock("../trust-surface", () => ({
  TrustSurfaceBlock: () => <div data-testid="mock-trust-surface" />,
}));
vi.mock("../what-changed", () => ({
  CountryWhatChanged: () => <div data-testid="mock-what-changed" />,
}));

type CountryReadModelResponse =
  components["schemas"]["CountryReadModelResponse"];

const card = {
  country: { slug: "argentina", name: "Аргентина" },
  profile: { executive_summary: "Краткое резюме по Аргентине." },
  scores: [],
  legal_signals: [],
  sources: [],
  evidence_summary: { total_evidence_count: 0, sources_by_type: {} },
  user_stories_summary: { total_count: 0, recent: [] },
  cii: null,
  meta: {},
  locale: { requested: "ru", resolved: "ru", is_fallback: false },
} as unknown as CountryReadModelResponse;

describe("CountryDossier — tabbed layout (web_dossier_v2)", () => {
  it("defaults to the overview tab and lists all 5 tab triggers", () => {
    renderWithProviders(
      <CountryDossier
        card={card}
        locale="ru"
      />,
    );

    expect(screen.getByTestId("country-dossier-tabs")).toBeInTheDocument();
    for (const [tabId, label] of Object.entries({
      overview: "Обзор",
      scores: "Оценки",
      trust: "Доверие",
      signals: "Сигналы",
      community: "Сообщество",
    })) {
      expect(screen.getByTestId(`dossier-tab-${tabId}`)).toHaveTextContent(
        label,
      );
    }
    expect(screen.getByTestId("dossier-tab-panel-overview")).toBeVisible();
    expect(screen.getByTestId("dossier-tab-panel-scores")).not.toBeVisible();
  });

  it("switching to a tab shows only that tab's sections in the panel and rail", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CountryDossier
        card={card}
        locale="ru"
      />,
    );

    await user.click(screen.getByTestId("dossier-tab-scores"));

    const panel = screen.getByTestId("dossier-tab-panel-scores");
    expect(panel).toBeVisible();
    expect(within(panel).getByTestId("mock-platform-intel")).toBeVisible();
    expect(within(panel).getByTestId("mock-drift")).toBeVisible();

    expect(screen.getByTestId("dossier-tab-panel-overview")).not.toBeVisible();

    // The rail only lists the active tab's sections (platform-intelligence,
    // drift, scores) -- not overview-tab sections like "cii" or "profile".
    expect(
      screen.getByTestId("dossier-rail-link-platform-intelligence"),
    ).toBeInTheDocument();
    expect(
      screen.queryByTestId("dossier-rail-link-cii"),
    ).not.toBeInTheDocument();
  });

  it("switching to the community tab renders its mocked blocks", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <CountryDossier
        card={card}
        locale="ru"
      />,
    );

    await user.click(screen.getByTestId("dossier-tab-community"));

    const panel = screen.getByTestId("dossier-tab-panel-community");
    expect(within(panel).getByTestId("mock-community")).toBeVisible();
    expect(within(panel).getByTestId("mock-migration-board")).toBeVisible();
  });
});
