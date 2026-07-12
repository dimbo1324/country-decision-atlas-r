import type { Meta, StoryObj } from "@storybook/react";
import { Dialog, DialogContent, DialogTrigger } from "./Dialog";
import { Button } from "./Button";

const meta: Meta<typeof Dialog> = {
  title: "Primitives/Dialog",
};
export default meta;
type Story = StoryObj<typeof Dialog>;

export const Default: Story = {
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Открыть диалог</Button>
      </DialogTrigger>
      <DialogContent
        title="Подтвердите действие"
        description="Это действие отзовёт все активные сессии на других устройствах."
      >
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 16 }}>
          <Button variant="ghost">Отмена</Button>
          <Button variant="primary">Подтвердить</Button>
        </div>
      </DialogContent>
    </Dialog>
  ),
};
