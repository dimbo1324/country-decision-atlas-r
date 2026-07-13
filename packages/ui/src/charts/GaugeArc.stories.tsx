import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { GaugeArc } from "./GaugeArc";

const meta: Meta<typeof GaugeArc> = {
  title: "Charts/GaugeArc",
  component: GaugeArc,
};
export default meta;
type Story = StoryObj<typeof GaugeArc>;

const baseArgs = {
  value: 42,
  label: "Риск сценария",
  accent: "terra" as const,
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
      <GaugeArc {...args} />
    </ForceReducedMotion>
  ),
};
