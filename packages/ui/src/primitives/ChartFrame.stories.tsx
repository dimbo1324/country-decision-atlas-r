import type { Meta, StoryObj } from "@storybook/react";
import { ChartFrame, MetricStat } from "./ChartFrame";

const meta: Meta<typeof ChartFrame> = {
  title: "Primitives/ChartFrame",
  component: ChartFrame,
};
export default meta;
type Story = StoryObj<typeof ChartFrame>;

export const Live: Story = {
  args: { title: "Скор доверия · 12 месяцев", live: true },
  render: (args) => (
    <div style={{ width: 360, height: 220 }}>
      <ChartFrame {...args}>
        <div
          style={{
            display: "flex",
            height: "100%",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--color-c4)",
          }}
        >
          график
        </div>
      </ChartFrame>
    </div>
  ),
};

export const Expandable: Story = {
  args: {
    title: "Развернуть для деталей (нажмите на иконку)",
    expandable: true,
    live: false,
  },
  render: (args) => (
    <div style={{ width: 360, height: 220 }}>
      <ChartFrame {...args}>
        <div
          style={{
            display: "flex",
            height: "100%",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--color-c4)",
          }}
        >
          график
        </div>
      </ChartFrame>
    </div>
  ),
};

export const WithTransparencyBadges: Story = {
  args: {
    title: "CII · профиль страны",
    live: false,
    verifiedAt: "2026-06",
    confidence: "high",
  },
  render: (args) => (
    <div style={{ width: 420, height: 220 }}>
      <ChartFrame {...args}>
        <div
          style={{
            display: "flex",
            height: "100%",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--color-c4)",
          }}
        >
          график
        </div>
      </ChartFrame>
    </div>
  ),
};

export const Stat: StoryObj<typeof MetricStat> = {
  render: () => (
    <MetricStat
      value="71"
      label="Скор доверия"
    />
  ),
};
