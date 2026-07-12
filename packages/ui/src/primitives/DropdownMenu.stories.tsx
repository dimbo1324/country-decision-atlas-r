import type { Meta, StoryObj } from "@storybook/react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./DropdownMenu";
import { Button } from "./Button";

const meta: Meta<typeof DropdownMenu> = {
  title: "Primitives/DropdownMenu",
};
export default meta;
type Story = StoryObj<typeof DropdownMenu>;

export const Default: Story = {
  render: () => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost">Действия ⌄</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuLabel>Страна</DropdownMenuLabel>
        <DropdownMenuItem>В сравнение</DropdownMenuItem>
        <DropdownMenuItem>В watchlist</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Сообщить об ошибке</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ),
};
