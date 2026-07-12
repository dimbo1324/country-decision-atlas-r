import type { Meta, StoryObj } from "@storybook/react";
import { Counter } from "./Counter";

const meta: Meta<typeof Counter> = {
  title: "Primitives/Counter",
  component: Counter,
};
export default meta;
type Story = StoryObj<typeof Counter>;

export const CountsUpOnMount: Story = {
  args: { value: 71, suffix: "%", active: true },
  render: (args) => (
    <span
      style={{
        fontFamily: "var(--font-display)",
        fontSize: 40,
        fontWeight: 700,
        color: "var(--color-gold3)",
      }}
    >
      <Counter {...args} />
    </span>
  ),
};
