import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { FilterChipGroup } from "./FilterChipGroup";

const meta: Meta<typeof FilterChipGroup> = {
  title: "Primitives/FilterChipGroup",
  component: FilterChipGroup,
};
export default meta;
type Story = StoryObj<typeof FilterChipGroup>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [value, setValue] = useState("");
      return (
        <div style={{ maxWidth: 480 }}>
          <FilterChipGroup
            name="country"
            label="Страна"
            value={value}
            onChange={setValue}
            options={[
              { value: "", label: "Все страны" },
              { value: "argentina", label: "Аргентина" },
              { value: "russia", label: "Россия" },
              { value: "uruguay", label: "Уругвай" },
            ]}
          />
        </div>
      );
    }
    return <Demo />;
  },
};
