import type { Meta, StoryObj } from "@storybook/react";
import { Popover, PopoverContent, PopoverTrigger } from "./Popover";
import { Button } from "./Button";

const meta: Meta<typeof Popover> = {
  title: "Primitives/Popover",
};
export default meta;
type Story = StoryObj<typeof Popover>;

export const Default: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost">Из чего сложилось число?</Button>
      </PopoverTrigger>
      <PopoverContent>
        CII = 0.4×LVI + 0.35×SSRS + 0.25×CS, нормировано по историческому
        диапазону страны.
      </PopoverContent>
    </Popover>
  ),
};
