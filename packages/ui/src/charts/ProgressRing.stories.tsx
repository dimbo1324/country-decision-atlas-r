import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { ProgressRing } from "./ProgressRing";

const meta: Meta<typeof ProgressRing> = {
  title: "Charts/ProgressRing",
  component: ProgressRing,
};
export default meta;
type Story = StoryObj<typeof ProgressRing>;

const baseArgs = {
  value: 71,
  label: "Индекс доверия",
  accent: "gold" as const,
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
      <ProgressRing {...args} />
    </ForceReducedMotion>
  ),
};
