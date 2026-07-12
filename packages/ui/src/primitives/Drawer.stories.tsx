import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Drawer } from "./Drawer";
import { Button } from "./Button";

const meta: Meta<typeof Drawer> = {
  title: "Primitives/Drawer",
  component: Drawer,
};
export default meta;
type Story = StoryObj<typeof Drawer>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [open, setOpen] = useState(false);
      return (
        <>
          <Button onClick={() => setOpen(true)}>Открыть досье</Button>
          <Drawer
            open={open}
            onClose={() => setOpen(false)}
            accent="gold"
            eyebrow="Дрейф · REF № CA-014"
            title="Что изменилось"
          >
            <p style={{ color: "var(--color-c3)", fontSize: 14, lineHeight: 1.7 }}>
              Содержимое досье изменения: источники, даты, затронутые метрики.
            </p>
          </Drawer>
        </>
      );
    }
    return <Demo />;
  },
};
