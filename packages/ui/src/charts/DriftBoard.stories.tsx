import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { DriftBoard } from "./DriftBoard";
import type { DriftBoardRow } from "./types";

const rows: DriftBoardRow[] = [
  {
    slug: "karindor",
    name: "Кариндор",
    flag: "KDR",
    timeline: [1, 1.4, 1.2, 1.8, 2.1, 2.4, 2.6, 3.0],
    driftValue: 2.4,
    status: "pos",
    statusLabel: "Улучшается",
  },
  {
    slug: "aurelia",
    name: "Аврелия",
    flag: "AVR",
    timeline: [0.2, 0.4, 0.3, 0.6, 0.5, 0.8, 0.7, 0.9],
    driftValue: 0.9,
    status: "mild",
    statusLabel: "Умеренно вверх",
  },
  {
    slug: "vesmaria",
    name: "Весмария",
    flag: "VSM",
    timeline: [0, 0.1, -0.1, 0, 0.05, -0.05, 0, 0.1],
    driftValue: 0.1,
    status: "stable",
    statusLabel: "Стабильно",
  },
  {
    slug: "norvintia",
    name: "Норвинтия",
    flag: "NRV",
    timeline: [0, -0.5, -0.8, -1.2, -1.6, -1.9, -2.2, -2.5],
    driftValue: -2.5,
    status: "neg",
    statusLabel: "Ухудшается",
  },
];

const meta: Meta<typeof DriftBoard> = {
  title: "Charts/DriftBoard",
  component: DriftBoard,
};
export default meta;
type Story = StoryObj<typeof DriftBoard>;

export const Live: Story = {
  args: { rows, active: true, mode: "live" },
};

export const Static: Story = {
  args: { rows, active: true, mode: "static" },
};

export const ReducedMotion: Story = {
  args: { rows, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <DriftBoard {...args} />
    </ForceReducedMotion>
  ),
};
