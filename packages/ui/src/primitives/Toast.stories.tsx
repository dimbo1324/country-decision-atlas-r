import type { Meta, StoryObj } from "@storybook/react";
import { toast, Toaster } from "./Toast";
import { Button } from "./Button";

const meta: Meta = {
  title: "Primitives/Toast",
};
export default meta;
type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <>
      <Toaster />
      <div style={{ display: "flex", gap: 12 }}>
        <Button onClick={() => toast.success("Watchlist обновлён")}>
          Success
        </Button>
        <Button
          variant="ghost"
          onClick={() => toast.error("Не удалось отозвать сессию")}
        >
          Error
        </Button>
      </div>
    </>
  ),
};
