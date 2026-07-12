import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Toggle } from "./Toggle";

const meta: Meta<typeof Toggle> = {
  title: "Primitives/Toggle",
  component: Toggle,
};
export default meta;
type Story = StoryObj<typeof Toggle>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [checked, setChecked] = useState(false);
      return (
        <div style={{ maxWidth: 320 }}>
          <Toggle
            checked={checked}
            onChange={setChecked}
            label="Учитывать налоговое соглашение"
            hint="+8 к скору CBLC"
            accent="sage"
          />
        </div>
      );
    }
    return <Demo />;
  },
};
