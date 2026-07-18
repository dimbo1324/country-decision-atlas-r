import type { Meta, StoryObj } from "@storybook/react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./Tooltip";
import { Icon } from "./Icon";
import { Info } from "lucide-react";

const meta: Meta<typeof Tooltip> = {
  title: "Primitives/Tooltip",
};
export default meta;
type Story = StoryObj<typeof Tooltip>;

export const Default: Story = {
  render: () => (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            aria-label="Подробнее"
            style={{
              background: "none",
              border: "none",
              color: "var(--color-c2)",
            }}
          >
            <Icon icon={Info} />
          </button>
        </TooltipTrigger>
        <TooltipContent>Уверенность: высокая</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};
