import type { Meta, StoryObj } from "@storybook/react";
import { DataTable } from "./DataTable";

const meta: Meta<typeof DataTable> = {
  title: "Primitives/DataTable",
  component: DataTable,
};
export default meta;
type Story = StoryObj<typeof DataTable>;

export const Default: Story = {
  args: {
    columns: [
      { header: "Метрика" },
      { header: "Значение", align: "right", numeric: true },
      { header: "Тренд", align: "right" },
    ],
    rows: [
      ["Индекс CII", "71", "↑"],
      ["Скорость дрейфа", "0.34", "→"],
      ["Достоверность", "высокая", "↑"],
    ],
  },
};
