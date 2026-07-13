import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { DonutChart } from "./DonutChart";
import type { DonutSegment } from "./types";

const segments: DonutSegment[] = [
  { label: "Межд. организации", value: 34, accent: "gold" },
  { label: "Нац. реестры", value: 28, accent: "blue" },
  { label: "Правовые сигналы", value: 22, accent: "sage" },
  { label: "Сообщество", value: 16, accent: "plum" },
];

const meta: Meta<typeof DonutChart> = {
  title: "Charts/DonutChart",
  component: DonutChart,
};
export default meta;
type Story = StoryObj<typeof DonutChart>;

const baseArgs = {
  segments,
  centerValue: "84",
  centerLabel: "Индекс доверия",
};

export const Live: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
};

export const Static: Story = {
  args: { ...baseArgs, active: true, mode: "static" },
};

export const ReducedMotion: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <DonutChart {...args} />
    </ForceReducedMotion>
  ),
};
