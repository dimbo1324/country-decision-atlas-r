import type { Meta, StoryObj } from "@storybook/react";
import { expect, userEvent, waitFor, within } from "@storybook/test";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./Select";

const meta: Meta<typeof Select> = {
  title: "Primitives/Select",
};
export default meta;
type Story = StoryObj<typeof Select>;

export const Default: Story = {
  render: () => (
    <Select defaultValue="relocation">
      <SelectTrigger style={{ width: 240 }}>
        <SelectValue placeholder="Выберите сценарий" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="relocation">Переезд</SelectItem>
        <SelectItem value="residency">ВНЖ/гражданство</SelectItem>
        <SelectItem value="remote">Удалённая работа</SelectItem>
        <SelectItem value="business">Бизнес</SelectItem>
      </SelectContent>
    </Select>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const body = within(canvasElement.ownerDocument.body);

    await userEvent.click(canvas.getByRole("combobox"));
    const option = await body.findByRole("option", {
      name: "ВНЖ/гражданство",
    });
    await userEvent.click(option);

    await waitFor(() =>
      expect(canvas.getByRole("combobox")).toHaveTextContent(
        "ВНЖ/гражданство",
      ),
    );
  },
};
