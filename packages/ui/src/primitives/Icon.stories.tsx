import type { Meta, StoryObj } from "@storybook/react";
import { ShieldAlert } from "lucide-react";
import { Icon, IconFrame } from "./Icon";

const meta: Meta<typeof Icon> = {
  title: "Primitives/Icon",
  component: Icon,
};
export default meta;
type Story = StoryObj<typeof Icon>;

export const Bare: Story = {
  args: { icon: ShieldAlert, size: 20 },
};

export const Framed: Story = {
  render: () => (
    <IconFrame
      icon={ShieldAlert}
      size={18}
    />
  ),
};
