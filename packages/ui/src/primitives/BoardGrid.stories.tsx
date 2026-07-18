import type { Meta, StoryObj } from "@storybook/react";
import { BoardGrid } from "./BoardGrid";
import { Card } from "./Card";

const meta: Meta<typeof BoardGrid> = {
  title: "Primitives/BoardGrid",
  component: BoardGrid,
};
export default meta;
type Story = StoryObj<typeof BoardGrid>;

export const Interactive: Story = {
  render: () => (
    <BoardGrid>
      {["Аргентина", "Россия", "Уругвай"].map((name) => (
        <Card
          key={name}
          interactive={false}
        >
          <span className="font-display text-lg font-semibold">{name}</span>
        </Card>
      ))}
    </BoardGrid>
  ),
};
