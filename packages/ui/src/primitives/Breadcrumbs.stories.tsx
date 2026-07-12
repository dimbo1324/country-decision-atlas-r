import type { Meta, StoryObj } from "@storybook/react";
import { Breadcrumbs } from "./Breadcrumbs";

const meta: Meta<typeof Breadcrumbs> = {
  title: "Primitives/Breadcrumbs",
  component: Breadcrumbs,
};
export default meta;
type Story = StoryObj<typeof Breadcrumbs>;

export const Default: Story = {
  args: {
    items: [
      { label: "Каталог", href: "/countries" },
      { label: "Норвинтия", href: "/countries/norvintia" },
      { label: "Доверие" },
    ],
  },
};
