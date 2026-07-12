import type { Meta, StoryObj } from "@storybook/react";
import { Skeleton } from "./Skeleton";

const meta: Meta<typeof Skeleton> = {
  title: "Primitives/Skeleton",
  component: Skeleton,
};
export default meta;
type Story = StoryObj<typeof Skeleton>;

export const ThreeLines: Story = {
  args: { lines: 3 },
  render: (args) => (
    <div style={{ maxWidth: 320 }}>
      <Skeleton {...args} />
    </div>
  ),
};
