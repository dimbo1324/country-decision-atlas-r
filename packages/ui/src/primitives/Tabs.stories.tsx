import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, waitFor, within } from "@storybook/test";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./Tabs";

const meta: Meta<typeof Tabs> = {
  title: "Primitives/Tabs",
};
export default meta;
type Story = StoryObj<typeof Tabs>;

export const Default: Story = {
  render: () => (
    <Tabs defaultValue="overview">
      <TabsList>
        <TabsTrigger value="overview">Обзор</TabsTrigger>
        <TabsTrigger value="cii">CII</TabsTrigger>
        <TabsTrigger value="trust">Доверие</TabsTrigger>
      </TabsList>
      <TabsContent value="overview">Обзор досье страны.</TabsContent>
      <TabsContent value="cii">Разбор индекса CII по компонентам.</TabsContent>
      <TabsContent value="trust">
        Скор доверия и структура источников.
      </TabsContent>
    </Tabs>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.getByText("Обзор досье страны.")).toBeVisible();

    await userEvent.click(canvas.getByRole("tab", { name: "CII" }));

    await waitFor(() =>
      expect(
        canvas.getByText("Разбор индекса CII по компонентам."),
      ).toBeVisible(),
    );
  },
};

const DOSSIER_TABS = [
  { id: "overview", label: "Обзор" },
  { id: "scores", label: "Оценки" },
  { id: "trust", label: "Доверие" },
  { id: "signals", label: "Сигналы" },
  { id: "community", label: "Сообщество" },
] as const;

/** Mirrors `CountryDossier`'s actual usage: `value`/`onValueChange`
 * controlled by external state (there, nuqs's URL `tab` param) rather than
 * `defaultValue`'s uncontrolled mode. */
function ControlledFiveTabDossier() {
  const [active, setActive] =
    useState<(typeof DOSSIER_TABS)[number]["id"]>("overview");
  return (
    <Tabs
      value={active}
      onValueChange={(value) => setActive(value as typeof active)}
    >
      <TabsList>
        {DOSSIER_TABS.map((tab) => (
          <TabsTrigger
            key={tab.id}
            value={tab.id}
          >
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {DOSSIER_TABS.map((tab) => (
        <TabsContent
          key={tab.id}
          value={tab.id}
        >
          Содержимое таба «{tab.label}».
        </TabsContent>
      ))}
    </Tabs>
  );
}

export const ControlledFiveTabs: Story = {
  render: () => <ControlledFiveTabDossier />,
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    expect(canvas.getByText("Содержимое таба «Обзор».")).toBeVisible();

    await userEvent.click(canvas.getByRole("tab", { name: "Сигналы" }));
    await waitFor(() =>
      expect(canvas.getByText("Содержимое таба «Сигналы».")).toBeVisible(),
    );

    await userEvent.click(canvas.getByRole("tab", { name: "Сообщество" }));
    await waitFor(() =>
      expect(canvas.getByText("Содержимое таба «Сообщество».")).toBeVisible(),
    );
  },
};
