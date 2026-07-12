import type { Meta, StoryObj } from "@storybook/react";
import { ErrorState } from "./ErrorState";

const meta: Meta<typeof ErrorState> = {
  title: "Primitives/ErrorState",
  component: ErrorState,
};
export default meta;
type Story = StoryObj<typeof ErrorState>;

export const Default: Story = {
  args: {
    title: "Что-то пошло не так",
    code: "ERR_COUNTRY_NOT_FOUND",
    message: "Не удалось загрузить досье страны. Повторите попытку позже.",
  },
};

export const BackendDown: Story = {
  args: {
    title: "Backend недоступен",
    message: "API недоступен. Убедитесь, что backend запущен, и повторите попытку.",
  },
};
