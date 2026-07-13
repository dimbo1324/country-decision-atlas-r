import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { RadarChart, type RadarSeries } from "./RadarChart";

const axes = [
  "Стабильность",
  "Верховенство закона",
  "Эконом. свобода",
  "Стоимость жизни",
  "ВНЖ",
  "Качество жизни",
];

const series: RadarSeries[] = [
  { label: "Кариндор", values: [72, 65, 58, 61, 80, 74], accent: "gold" },
  { label: "Аврелия", values: [54, 70, 82, 40, 63, 69], accent: "blue" },
];

const meta: Meta<typeof RadarChart> = {
  title: "Charts/RadarChart",
  component: RadarChart,
};
export default meta;
type Story = StoryObj<typeof RadarChart>;

export const Live: Story = {
  args: { axes, series, active: true, mode: "live" },
  render: (args) => (
    <div style={{ width: 380, height: 380 }}>
      <RadarChart {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { axes, series, active: true, mode: "static" },
  render: (args) => (
    <div style={{ width: 380, height: 380 }}>
      <RadarChart {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { axes, series, active: true, mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 380, height: 380 }}>
        <RadarChart {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
