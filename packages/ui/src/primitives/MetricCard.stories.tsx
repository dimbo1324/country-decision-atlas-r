import type { Meta, StoryObj } from "@storybook/react";
import { Zap } from "lucide-react";
import { MetricCard } from "./MetricCard";

const meta: Meta<typeof MetricCard> = {
  title: "Primitives/MetricCard",
  component: MetricCard,
};
export default meta;
type Story = StoryObj<typeof MetricCard>;

export const Default: Story = {
  args: {
    icon: Zap,
    name: "Legal Velocity Index",
    tag: "LVI · собственная метрика",
    description: "Скорость изменения правового поля за последние 12 месяцев.",
    value: "0.62",
    unit: "индекс",
    accent: "gold",
  },
  render: (args) => (
    <div style={{ maxWidth: 280 }}>
      <MetricCard {...args} />
    </div>
  ),
};
