import type { Meta, StoryObj } from "@storybook/react";
import { TimelineList } from "./TimelineList";

const meta: Meta<typeof TimelineList> = {
  title: "Primitives/TimelineList",
  component: TimelineList,
};
export default meta;
type Story = StoryObj<typeof TimelineList>;

export const Default: Story = {
  args: {
    events: [
      {
        id: "1",
        date: "2026-07-01",
        impact: "up",
        impactLabel: "Индекс CII вырос на 4 пункта",
        title: "Пересмотр визовой политики",
        source: "MOI",
      },
      {
        id: "2",
        date: "2026-06-18",
        impact: "down",
        impactLabel: "Снижение скора доверия",
        title: "Новый правовой сигнал",
        source: "GOV",
      },
      {
        id: "3",
        date: "2026-06-02",
        impact: "info",
        impactLabel: "Без изменения скора",
        title: "Обновлена методология",
        source: "CDA",
      },
    ],
  },
  render: (args) => (
    <div style={{ maxWidth: 480 }}>
      <TimelineList {...args} />
    </div>
  ),
};
