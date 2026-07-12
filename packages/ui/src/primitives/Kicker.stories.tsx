import type { Meta, StoryObj } from "@storybook/react";
import { Kicker } from "./Kicker";

const meta: Meta<typeof Kicker> = {
  title: "Primitives/Kicker",
  component: Kicker,
};
export default meta;
type Story = StoryObj<typeof Kicker>;

export const Default: Story = {
  args: { children: "Собственный интеллект" },
};

export const AllAccents: Story = {
  render: () => (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {(["gold", "blue", "terra", "sage", "plum"] as const).map((accent) => (
        <Kicker
          key={accent}
          accent={accent}
        >
          {accent}
        </Kicker>
      ))}
    </div>
  ),
};
