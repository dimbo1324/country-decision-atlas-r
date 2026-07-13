import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { BarColumns } from "./BarColumns";

const items = [
  { label: "Релокация", value: 62 },
  { label: "Резидентство", value: 74 },
  { label: "Бизнес", value: 48 },
  { label: "Низкий бюджет", value: 55 },
];

const meta: Meta<typeof BarColumns> = {
  title: "Charts/BarColumns",
  component: BarColumns,
};
export default meta;
type Story = StoryObj<typeof BarColumns>;

export const Live: Story = {
  args: { items, active: true, accent: "blue", mode: "live" },
  render: (args) => (
    <div style={{ width: 360, height: 220 }}>
      <BarColumns {...args} />
    </div>
  ),
};

export const Static: Story = {
  args: { items, active: true, accent: "blue", mode: "static" },
  render: (args) => (
    <div style={{ width: 360, height: 220 }}>
      <BarColumns {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { items, active: true, accent: "blue", mode: "live" },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 360, height: 220 }}>
        <BarColumns {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
