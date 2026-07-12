import type { Meta, StoryObj } from "@storybook/react";
import { Button } from "./Button";

const meta: Meta<typeof Button> = {
  title: "Primitives/Button",
  component: Button,
};
export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: { variant: "primary", children: "Запустить анализ" },
};

export const Ghost: Story = {
  args: { variant: "ghost", children: "Подробнее" },
};

export const Disabled: Story = {
  args: { variant: "primary", children: "Недоступно", disabled: true },
};
