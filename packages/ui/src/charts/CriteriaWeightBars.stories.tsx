import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { CriteriaWeightBars } from "./CriteriaWeightBars";
import type { CriteriaWeight } from "./types";

const criteria: CriteriaWeight[] = [
  { label: "Стоимость жизни", contribution: 14 },
  { label: "Верховенство закона", contribution: 9 },
  { label: "ВНЖ / визы", contribution: 6 },
  { label: "Налоговый режим", contribution: -4 },
  { label: "Дрейф законодательства", contribution: -11 },
];

const meta: Meta<typeof CriteriaWeightBars> = {
  title: "Charts/CriteriaWeightBars",
  component: CriteriaWeightBars,
};
export default meta;
type Story = StoryObj<typeof CriteriaWeightBars>;

export const Default: Story = {
  args: { criteria, active: true },
  render: (args) => (
    <div style={{ width: 420 }}>
      <CriteriaWeightBars {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { criteria, active: true },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 420 }}>
        <CriteriaWeightBars {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
