import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { DivergingMeter } from "./DivergingMeter";

const meta: Meta<typeof DivergingMeter> = {
  title: "Charts/DivergingMeter",
  component: DivergingMeter,
};
export default meta;
type Story = StoryObj<typeof DivergingMeter>;

const baseArgs = {
  categories: ["Релокация", "Резидентство", "Бизнес", "Низкий бюджет"],
  leftLabel: "Кариндор",
  rightLabel: "Аврелия",
  leftValues: [72, 65, 58, 61],
  rightValues: [54, 70, 82, 40],
  leftAccent: "gold" as const,
  rightAccent: "blue" as const,
};

export const Live: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <DivergingMeter {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { ...baseArgs, active: true, mode: "static" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <DivergingMeter {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 460, height: 260 }}>
        <DivergingMeter {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
