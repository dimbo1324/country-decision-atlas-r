import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Slider } from "./Slider";

const meta: Meta<typeof Slider> = {
  title: "Primitives/Slider",
  component: Slider,
};
export default meta;
type Story = StoryObj<typeof Slider>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [value, setValue] = useState([40]);
      return (
        <div style={{ width: 280 }}>
          <Slider
            accent="gold"
            value={value}
            onValueChange={setValue}
            max={100}
            step={1}
          />
          <p style={{ color: "var(--color-c3)", fontSize: 12, marginTop: 8 }}>
            Вес критерия: {value[0]}
          </p>
        </div>
      );
    }
    return <Demo />;
  },
};
