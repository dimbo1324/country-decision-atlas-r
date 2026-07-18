import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { RadioCards } from "./RadioCards";

const meta: Meta<typeof RadioCards> = {
  title: "Primitives/RadioCards",
  component: RadioCards,
};
export default meta;
type Story = StoryObj<typeof RadioCards>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [value, setValue] = useState("relocation");
      return (
        <div style={{ maxWidth: 480 }}>
          <RadioCards
            name="scenario"
            value={value}
            onChange={setValue}
            accent="gold"
            options={[
              {
                value: "relocation",
                label: "Переезд",
                description: "Полная смена страны проживания",
              },
              {
                value: "residency",
                label: "ВНЖ/гражданство",
                description: "Легальный статус без переезда сразу",
              },
              {
                value: "remote",
                label: "Удалённая работа",
                description: "Виза цифрового кочевника",
              },
              {
                value: "business",
                label: "Бизнес",
                description: "Регистрация и налоговый режим",
              },
            ]}
          />
        </div>
      );
    }
    return <Demo />;
  },
};
