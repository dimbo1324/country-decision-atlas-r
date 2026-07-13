import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { SparklineChart } from "./SparklineChart";

const values = [3.2, 3.6, 3.4, 4.1, 4.8, 4.6, 5.2, 5.0, 5.6, 6.1, 5.8, 6.4];

const meta: Meta<typeof SparklineChart> = {
  title: "Charts/SparklineChart",
  component: SparklineChart,
};
export default meta;
type Story = StoryObj<typeof SparklineChart>;

const baseArgs = {
  values,
  accent: "gold" as const,
  yAxisLabel: "Индекс скорости права",
  xAxisLabel: "12 кварталов",
};

export const Live: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
  render: (args) => (
    <div style={{ width: 420, height: 220 }}>
      <SparklineChart {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { ...baseArgs, active: true, mode: "static" },
  render: (args) => (
    <div style={{ width: 420, height: 220 }}>
      <SparklineChart {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { ...baseArgs, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 420, height: 220 }}>
        <SparklineChart {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
