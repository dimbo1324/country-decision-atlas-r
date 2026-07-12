import type { Meta, StoryObj } from "@storybook/react";
import { Accordion } from "./Accordion";

const meta: Meta<typeof Accordion> = {
  title: "Primitives/Accordion",
  component: Accordion,
};
export default meta;
type Story = StoryObj<typeof Accordion>;

export const Default: Story = {
  args: {
    items: [
      {
        title: "Как считается скор CBLC",
        meta: "Методология",
        content: "Базовый скор совместимости пары юрисдикций плюс явные бонусы.",
      },
      {
        title: "Откуда данные",
        meta: "Источники",
        content: "Каждая ячейка подкреплена источником с датой верификации.",
      },
      {
        title: "Что не входит в скор",
        meta: "Границы",
        content: "Репутация и донаты никогда не влияют на скор.",
      },
    ],
  },
  render: (args) => (
    <div style={{ maxWidth: 420 }}>
      <Accordion {...args} />
    </div>
  ),
};
