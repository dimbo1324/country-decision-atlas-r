import type { Meta, StoryObj } from "@storybook/react";
import { SignalTicker } from "./SignalTicker";

const meta: Meta<typeof SignalTicker> = {
  title: "Primitives/SignalTicker",
  component: SignalTicker,
};
export default meta;
type Story = StoryObj<typeof SignalTicker>;

export const Default: Story = {
  args: {
    items: [
      "Норвинтия · пересмотр визовой политики",
      "Эстарра · новый налоговый сигнал",
      "Каррия · обновлена методология CII",
      "Вальдория · рост скора доверия",
    ],
  },
};
