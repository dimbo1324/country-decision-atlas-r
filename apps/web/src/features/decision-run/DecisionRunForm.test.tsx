import {
  afterAll,
  afterEach,
  beforeAll,
  describe,
  expect,
  it,
  vi,
} from "vitest";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import { renderWithProviders } from "../../test-utils/render";
import { DecisionRunForm } from "./DecisionRunForm";

vi.mock("../../shared/lib/useAppLocale", () => ({
  useAppLocale: () => "ru",
}));
vi.mock("../../shared/analytics/useAnalyticsEvent", () => ({
  useAnalyticsEvent: () => vi.fn(),
}));
vi.mock("../decision-wizard", () => ({
  DecisionWizard: () => <div data-testid="mock-decision-wizard" />,
}));
vi.mock("../ai-assistant", () => ({
  AIDecisionIntentHelper: () => <div data-testid="mock-ai-helper" />,
}));
vi.mock("../decision-passports", () => ({
  DecisionPassportActions: () => null,
}));
vi.mock("../decision-visual-comparison", () => ({
  DecisionCiiComparison: () => null,
}));
vi.mock("../platform-intelligence", () => ({
  DecisionRiskContext: () => null,
}));
vi.mock("./DecisionResults", () => ({
  DecisionResults: () => <div data-testid="mock-decision-results" />,
}));

const API_BASE_URL = "http://localhost:8000";

const countriesResponse = {
  items: [
    { slug: "russia", name: "Россия" },
    { slug: "uruguay", name: "Уругвай" },
    { slug: "argentina", name: "Аргентина" },
  ],
};

const scenariosResponse = {
  items: [
    { slug: "relocation_residence", name: "Релокация и ВНЖ" },
    { slug: "business_self_employment", name: "Бизнес и самозанятость" },
  ],
};

const personasResponse = { items: [] };

const server = setupServer(
  http.get(`${API_BASE_URL}/api/v1/countries`, () =>
    HttpResponse.json(countriesResponse),
  ),
  http.get(`${API_BASE_URL}/api/v1/scenarios`, () =>
    HttpResponse.json(scenariosResponse),
  ),
  http.get(`${API_BASE_URL}/api/v1/personas`, () =>
    HttpResponse.json(personasResponse),
  ),
);

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

async function renderForm() {
  renderWithProviders(<DecisionRunForm />);
  await screen.findByTestId("decision-run-wizard");
}

describe("DecisionRunForm — 4-step wizard", () => {
  it("renders all 4 step labels with step 1 active by default", async () => {
    await renderForm();

    expect(screen.getByTestId("decision-step-1")).toHaveAttribute(
      "aria-current",
      "step",
    );
    expect(screen.getByTestId("decision-step-2")).not.toHaveAttribute(
      "aria-current",
    );
    expect(screen.getByTestId("decision-step-panel-1")).toBeVisible();

    const nav = screen.getByRole("navigation", { name: "Шаги подбора" });
    expect(within(nav).getByText("Цель")).toBeInTheDocument();
    expect(within(nav).getByText("Откуда")).toBeInTheDocument();
    expect(within(nav).getByText("Приоритеты")).toBeInTheDocument();
    expect(within(nav).getByText("Запуск")).toBeInTheDocument();
  });

  it("advances via 'Далее' and shows the matching panel each step", async () => {
    const user = userEvent.setup();
    await renderForm();

    await user.click(screen.getByTestId("decision-step-next"));
    expect(screen.getByTestId("decision-step-panel-2")).toBeVisible();
    expect(screen.getByTestId("decision-step-2")).toHaveAttribute(
      "aria-current",
      "step",
    );

    await user.click(screen.getByTestId("decision-step-next"));
    expect(screen.getByTestId("decision-step-panel-3")).toBeVisible();

    await user.click(screen.getByTestId("decision-step-next"));
    expect(screen.getByTestId("decision-step-panel-4")).toBeVisible();
    expect(screen.getByTestId("decision-step-next")).toBeDisabled();
  });

  it("jumps directly to a step via its nav button", async () => {
    const user = userEvent.setup();
    await renderForm();

    await user.click(screen.getByTestId("decision-step-3"));
    expect(screen.getByTestId("decision-step-panel-3")).toBeVisible();
    expect(screen.getByTestId("decision-step-prev")).not.toBeDisabled();
  });

  it("'Назад' is disabled on step 1 and re-enables after moving forward", async () => {
    const user = userEvent.setup();
    await renderForm();

    expect(screen.getByTestId("decision-step-prev")).toBeDisabled();
    await user.click(screen.getByTestId("decision-step-next"));
    expect(screen.getByTestId("decision-step-prev")).not.toBeDisabled();
  });

  it("disables the run button once every candidate country is unchecked", async () => {
    const user = userEvent.setup();
    await renderForm();

    await user.click(screen.getByTestId("decision-step-2"));
    await waitFor(() =>
      expect(screen.getByTestId("decision-step-panel-2")).toBeVisible(),
    );

    for (const name of ["Россия", "Уругвай"]) {
      await user.click(screen.getByRole("checkbox", { name }));
    }

    await user.click(screen.getByTestId("decision-step-4"));
    expect(screen.getByTestId("decision-run-button")).toBeDisabled();
  });
});
