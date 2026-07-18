import type { Meta, StoryObj } from "@storybook/react";
import { Card } from "./Card";

const meta: Meta<typeof Card> = {
  title: "Primitives/Card",
  component: Card,
  argTypes: {
    accent: {
      control: "select",
      options: ["gold", "blue", "terra", "sage", "plum"],
    },
  },
};
export default meta;
type Story = StoryObj<typeof Card>;

export const Gold: Story = {
  args: {
    accent: "gold",
    children: "Наведите курсор — лазерная обводка бежит по периметру.",
  },
};

export const AllAccents: Story = {
  render: () => (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: 16,
      }}
    >
      {(["gold", "blue", "terra", "sage", "plum"] as const).map((accent) => (
        <Card
          key={accent}
          accent={accent}
        >
          {accent}
        </Card>
      ))}
    </div>
  ),
};

export const Clickable: Story = {
  args: {
    accent: "sage",
    onClick: () => alert("card clicked"),
    children: "Кликабельная карточка (role=button)",
  },
};

export const NonInteractive: Story = {
  args: {
    interactive: false,
    children: "Без лазерной обводки при наведении",
  },
};
