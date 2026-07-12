import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Pagination } from "./Pagination";

const meta: Meta<typeof Pagination> = {
  title: "Primitives/Pagination",
  component: Pagination,
};
export default meta;
type Story = StoryObj<typeof Pagination>;

export const Interactive: Story = {
  render: () => {
    function Demo() {
      const [page, setPage] = useState(3);
      return (
        <Pagination
          page={page}
          pageCount={12}
          onPageChange={setPage}
        />
      );
    }
    return <Demo />;
  },
};
