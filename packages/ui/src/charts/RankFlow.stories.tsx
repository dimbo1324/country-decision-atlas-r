import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { RankFlow } from "./RankFlow";
import type { RankFlowSeries } from "./types";

const columns = ["К1'25", "К2'25", "К3'25", "К4'25", "К1'26"];
const series: RankFlowSeries[] = [
  { name: "Кариндор", accent: "gold", ranks: [2, 1, 1, 2, 1] },
  { name: "Аврелия", accent: "blue", ranks: [1, 2, 3, 1, 2] },
  { name: "Весмария", accent: "terra", ranks: [3, 3, 2, 3, 3] },
];

const meta: Meta<typeof RankFlow> = {
  title: "Charts/RankFlow",
  component: RankFlow,
};
export default meta;
type Story = StoryObj<typeof RankFlow>;

export const Live: Story = {
  args: { series, columns, active: true, mode: "live" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <RankFlow {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { series, columns, active: true, mode: "static" },
  render: (args) => (
    <div style={{ width: 460, height: 260 }}>
      <RankFlow {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { series, columns, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 460, height: 260 }}>
        <RankFlow {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
