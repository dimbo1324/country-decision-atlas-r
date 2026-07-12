import type { Meta, StoryObj } from "@storybook/react";
import { Badge, type BadgeVariant } from "./Badge";

const meta: Meta<typeof Badge> = {
  title: "Primitives/Badge",
  component: Badge,
};
export default meta;
type Story = StoryObj<typeof Badge>;

const VARIANTS: BadgeVariant[] = [
  "default",
  "positive",
  "negative",
  "warning",
  "critical",
  "info",
  "trust",
];

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
      {VARIANTS.map((variant) => (
        <Badge
          key={variant}
          variant={variant}
        >
          {variant}
        </Badge>
      ))}
    </div>
  ),
};
