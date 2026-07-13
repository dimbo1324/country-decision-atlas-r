import type { Meta, StoryObj } from "@storybook/react";
import { PassportCard } from "./PassportCard";
import type { PassportData } from "./types";

const passport: PassportData = {
  reference: "CA-DP-2026-0412",
  fromName: "Кариндор",
  fromFlag: "KDR",
  toName: "Аврелия",
  toFlag: "AVR",
  baseScore: 64,
  taxTreatyBonus: 9,
  nomadBonus: 6,
  visaLabel: "Безвиз · 180 дней",
  timezoneShift: "+1ч",
  confidence: 0.88,
  verifiedOn: "2026-07",
};

const meta: Meta<typeof PassportCard> = {
  title: "Charts/PassportCard",
  component: PassportCard,
};
export default meta;
type Story = StoryObj<typeof PassportCard>;

export const Default: Story = {
  args: { passport, active: true },
  render: (args) => (
    <div style={{ width: 560 }}>
      <PassportCard {...args} />
    </div>
  ),
};
