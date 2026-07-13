import type { Meta, StoryObj } from "@storybook/react";
import { ForceReducedMotion } from "../../.storybook/ForceReducedMotion";
import { LegalSignalTimeline } from "./LegalSignalTimeline";
import type { LegalSignalEvent } from "./types";

const events: LegalSignalEvent[] = [
  {
    id: "sig-1",
    date: "2026-01-14",
    country: "Кариндор",
    title: "Упрощение визового режима для специалистов",
    impact: "up",
    impactLabel: "Позитивно · релокация, найм",
  },
  {
    id: "sig-2",
    date: "2026-02-28",
    country: "Аврелия",
    title: "Ограничение иностранных счетов",
    impact: "down",
    impactLabel: "Высокое влияние · инвесторы",
  },
  {
    id: "sig-3",
    date: "2026-04-10",
    country: "Кариндор",
    title: "Снижение корп. налога",
    impact: "up",
    impactLabel: "Позитивно · бизнес, фриланс",
  },
  {
    id: "sig-4",
    date: "2026-05-22",
    country: "Весмария",
    title: "Дрейф сменился на «умеренно вверх»",
    impact: "info",
    impactLabel: "Смена дрейфа · алерт подписчикам",
  },
  {
    id: "sig-5",
    date: "2026-06-30",
    country: "Аврелия",
    title: "Новая программа ВНЖ за инвестиции",
    impact: "up",
    impactLabel: "Позитивно · резидентство",
  },
];

const meta: Meta<typeof LegalSignalTimeline> = {
  title: "Charts/LegalSignalTimeline",
  component: LegalSignalTimeline,
};
export default meta;
type Story = StoryObj<typeof LegalSignalTimeline>;

export const Default: Story = {
  args: { events, active: true },
  render: (args) => (
    <div style={{ width: 760, height: 180 }}>
      <LegalSignalTimeline {...args} />
    </div>
  ),
};

export const ReducedMotion: Story = {
  args: { events, active: true },
  render: (args) => (
    <ForceReducedMotion>
      <div style={{ width: 760, height: 180 }}>
        <LegalSignalTimeline {...args} />
      </div>
    </ForceReducedMotion>
  ),
};
