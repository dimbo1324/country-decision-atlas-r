import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { Heatmap } from "./Heatmap";
import type { HeatmapData } from "./types";

const data: HeatmapData = {
  rows: ["Кариндор", "Аврелия", "Весмария", "Норвинтия"],
  columns: ["Янв", "Фев", "Мар", "Апр", "Май", "Июн"],
  values: [
    [22, 30, 18, 40, 55, 60],
    [45, 38, 50, 62, 58, 70],
    [10, 15, 20, 12, 8, 18],
    [60, 65, 58, 72, 80, 75],
  ],
};

const meta: Meta<typeof Heatmap> = {
  title: "Charts/Heatmap",
  component: Heatmap,
};
export default meta;
type Story = StoryObj<typeof Heatmap>;

export const Live: Story = {
  args: { data, active: true, mode: "live" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <Heatmap {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { data, active: true, mode: "static" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <Heatmap {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { data, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 460, height: 260 }}>
        <Heatmap {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
